"""ChannelResolver unit tests — the channel abstraction (Phase 1 requirement)."""

import pytest

from domains.conversation.constants.conversation_constants import ConversationChannel
from domains.conversation.exceptions.conversation_exceptions import UnsupportedChannelError
from domains.conversation.services.channel_resolver import ChannelResolver


class TestChannelResolver:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("web_form", ConversationChannel.WEB_CHAT),
            ("web_chat", ConversationChannel.WEB_CHAT),
            ("voice", ConversationChannel.VOICE),
            ("phone", ConversationChannel.VOICE),
            ("whatsapp", ConversationChannel.WHATSAPP),
            ("email", ConversationChannel.EMAIL),
            ("complaint", ConversationChannel.COMPLAINT),
            ("WHATSAPP", ConversationChannel.WHATSAPP),
        ],
    )
    def test_resolve_known_channels(self, raw: str, expected: ConversationChannel) -> None:
        assert ChannelResolver.resolve(raw) == expected

    def test_resolve_unknown_channel_raises(self) -> None:
        with pytest.raises(UnsupportedChannelError):
            ChannelResolver.resolve("carrier_pigeon")
