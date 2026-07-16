import asyncio
from ai.providers.base import create_provider
from ai.models import ChatRequest, ChatMessage

async def main():
    p = create_provider('azure_openai')
    r = await p.chat(ChatRequest(messages=[ChatMessage(role='user', content='Hello')]))
    print(r.message.content)

asyncio.run(main())
