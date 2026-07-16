"""LiveKit Transport Layer.

Responsibilities:
    Join/Leave Room
    Audio Transport (publish/subscribe)
    Connection Status
    Reconnect Handling
    Session Metadata

No business logic — pure transport.
"""

import secrets
from datetime import timedelta
from typing import Any, Callable

from livekit import api as livekit_api
from livekit.protocol import models as livekit_models

from app.platform.logging import get_logger
from voice.config import VoiceConfig

logger = get_logger(__name__)


class ConnectionState:
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class LiveKitTransport:
    def __init__(self, config: VoiceConfig | None = None) -> None:
        self._config = config or VoiceConfig()
        self._url: str = self._config.livekit_url
        self._api_key: str = self._config.livekit_api_key
        self._api_secret: str = self._config.livekit_api_secret
        self._token_ttl = timedelta(hours=1)
        self._connection_state: str = ConnectionState.DISCONNECTED
        self._on_connection_change: Callable[[str], None] | None = None

    # ── Token Generation ──────────────────────────────────────────

    def _get_access_token(self) -> livekit_api.AccessToken:
        return livekit_api.AccessToken(self._api_key, self._api_secret)

    def _encode_token(self, token: livekit_api.AccessToken) -> str:
        """Encode an AccessToken to JWT, omitting the nbf claim
        to avoid clock skew issues with the LiveKit server."""
        import jwt as pyjwt
        from datetime import datetime, timezone
        claims = token.claims.asdict()
        claims.update({
            "sub": token.identity,
            "iss": token.api_key,
            "exp": int((datetime.now(timezone.utc) + token.ttl).timestamp()),
        })
        return pyjwt.encode(claims, token.api_secret, algorithm="HS256")

    def generate_agent_token(
        self,
        room_name: str,
        identity: str = "voice-agent",
        participant_name: str = "LuMay AI Voice Agent",
    ) -> str:
        from livekit.api.access_token import AccessToken, VideoGrants
        token = AccessToken(self._api_key, self._api_secret) \
            .with_identity(identity) \
            .with_name(participant_name) \
            .with_ttl(self._token_ttl) \
            .with_grants(VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            ))
        jwt = self._encode_token(token)
        logger.debug("livekit_agent_token_generated", room=room_name, identity=identity)
        return jwt

    def generate_participant_token(
        self,
        room_name: str,
        identity: str | None = None,
        participant_name: str | None = None,
        ttl_seconds: int = 3600,
    ) -> str:
        from livekit.api.access_token import AccessToken, VideoGrants
        ident = identity or f"caller-{secrets.token_hex(6)}"
        token = AccessToken(self._api_key, self._api_secret) \
            .with_identity(ident) \
            .with_name(participant_name or "Customer") \
            .with_ttl(timedelta(seconds=ttl_seconds)) \
            .with_grants(VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            ))
        jwt = self._encode_token(token)
        logger.debug("livekit_participant_token_generated", room=room_name, identity=ident)
        return jwt

    # ── Room Management ───────────────────────────────────────────

    def _api_url(self) -> str:
        return self._url.replace("wss://", "https://").replace("ws://", "http://")

    async def create_room(
        self,
        name: str,
        max_participants: int = 2,
        empty_timeout: int = 60,
    ) -> livekit_models.Room:
        from livekit.protocol import room as room_models
        from livekit.api import VideoGrants
        req = room_models.CreateRoomRequest(
            name=name,
            max_participants=max_participants,
            empty_timeout=empty_timeout,
        )
        try:
            import asyncio
            logger.info("livekit_room_creating", room=name, max_participants=max_participants)
            room = await asyncio.wait_for(
                self._twirp_request(
                    "RoomService", "CreateRoom", req, livekit_models.Room,
                    VideoGrants(room_create=True),
                ),
                timeout=10.0,
            )
            logger.info("livekit_room_created", room=name)
            return room
        except asyncio.TimeoutError:
            logger.error("livekit_room_creation_timeout", room=name)
            raise
        except Exception as e:
            logger.error("livekit_room_creation_failed", room=name, error=str(e))
            raise

    def _build_admin_token(self, grants: livekit_api.VideoGrants) -> str:
        """Build a JWT for LiveKit REST API calls without the nbf claim."""
        import jwt as pyjwt
        from datetime import datetime, timezone, timedelta
        from livekit.api.access_token import AccessToken
        token = AccessToken(self._api_key, self._api_secret)
        token.with_grants(grants)
        claims = token.claims.asdict()
        claims.update({
            "sub": "api",
            "iss": self._api_key,
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        })
        return pyjwt.encode(claims, self._api_secret, algorithm="HS256")

    async def _twirp_request(
        self,
        service: str,
        method: str,
        request_msg,
        response_class,
        grants: livekit_api.VideoGrants,
    ) -> any:
        """Make a Twirp RPC call to the LiveKit API with a properly signed token."""
        import aiohttp
        token = self._build_admin_token(grants)
        async with aiohttp.ClientSession() as session:
            url = f"{self._api_url()}/twirp/livekit.{service}/{method}"
            headers = {
                "Content-Type": "application/protobuf",
                "Authorization": f"Bearer {token}",
            }
            async with session.post(url, headers=headers, data=request_msg.SerializeToString()) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    return response_class.FromString(data)
                body = await resp.text()
                raise Exception(f"HTTP {resp.status}: {body[:200]}")

    async def delete_room(self, name: str) -> None:
        try:
            from livekit.protocol import room as room_models
            from livekit.api import VideoGrants
            req = room_models.DeleteRoomRequest(room=name)
            await self._twirp_request(
                "RoomService", "DeleteRoom", req, room_models.DeleteRoomResponse,
                VideoGrants(room_create=True),
            )
            logger.info("livekit_room_deleted", room=name)
        except Exception as exc:
            logger.warning("livekit_room_deletion_failed", room=name, error=str(exc))

    async def list_participants(self, room_name: str) -> list[livekit_models.ParticipantInfo]:
        from livekit.protocol import room as room_models
        from livekit.api import VideoGrants
        req = room_models.ListParticipantsRequest(room=room_name)
        resp = await self._twirp_request(
            "RoomService", "ListParticipants", req, room_models.ListParticipantsResponse,
            VideoGrants(room_admin=True, room=room_name),
        )
        return resp.participants

    async def remove_participant(self, room_name: str, identity: str) -> None:
        from livekit.protocol import room as room_models
        from livekit.api import VideoGrants
        req = room_models.RoomParticipantIdentity(room=room_name, identity=identity)
        await self._twirp_request(
            "RoomService", "RemoveParticipant", req, room_models.RemoveParticipantResponse,
            VideoGrants(room_admin=True, room=room_name),
        )
        logger.info("livekit_participant_removed", room=room_name, identity=identity)

    # ── Connection Monitoring ─────────────────────────────────────

    @property
    def connection_state(self) -> str:
        return self._connection_state

    def on_connection_change(self, callback: Callable[[str], None]) -> None:
        self._on_connection_change = callback

    def _set_connection_state(self, state: str) -> None:
        self._connection_state = state
        if self._on_connection_change:
            self._on_connection_change(state)

    # ── Session Metadata ──────────────────────────────────────────

    async def get_room_metadata(self, room_name: str) -> dict[str, Any]:
        try:
            async with livekit_api.LiveKitAPI(
                url=self._api_url(),
                api_key=self._api_key,
                api_secret=self._api_secret,
            ) as lk_api:
                room = await lk_api.rooms.get_room(room=room_name)
                return {
                    "name": room.name,
                    "participant_count": len(await self.list_participants(room_name)),
                    "creation_time": room.creation_time,
                    "empty_timeout": room.empty_timeout,
                }
        except Exception as exc:
            logger.warning("livekit_get_room_metadata_failed", room=room_name, error=str(exc))
            return {}
