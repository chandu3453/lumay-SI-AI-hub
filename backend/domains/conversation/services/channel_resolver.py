"""Channel abstraction — resolves the many raw channel strings used across the
codebase today (InteractionChannel values, complaint sources, ad hoc literals)
to the unified `ConversationChannel` enum.

Adding a new channel later (SMS, Teams, mobile app) means: one new
`ConversationChannel` enum value + one new entry in `_CHANNEL_MAP` here.
"""

from domains.conversation.constants.conversation_constants import ConversationChannel
from domains.conversation.exceptions.conversation_exceptions import UnsupportedChannelError

_CHANNEL_MAP: dict[str, ConversationChannel] = {
    "web_form": ConversationChannel.WEB_CHAT,
    "web_chat": ConversationChannel.WEB_CHAT,
    "webchat": ConversationChannel.WEB_CHAT,
    "voice": ConversationChannel.VOICE,
    "phone": ConversationChannel.VOICE,
    "whatsapp": ConversationChannel.WHATSAPP,
    "email": ConversationChannel.EMAIL,
    "complaint": ConversationChannel.COMPLAINT,
    "web_form_complaint": ConversationChannel.COMPLAINT,
}


class ChannelResolver:
    @staticmethod
    def resolve(raw_channel: str) -> ConversationChannel:
        normalized = (raw_channel or "").strip().lower()
        resolved = _CHANNEL_MAP.get(normalized)
        if resolved is None:
            raise UnsupportedChannelError(context={"raw_channel": raw_channel})
        return resolved
