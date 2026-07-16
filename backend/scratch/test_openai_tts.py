import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

async def main():
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY")
    print("OpenAI API Key configured:", bool(key), f"({len(key) if key else 0} chars)")
    
    client = AsyncOpenAI(api_key=key)
    try:
        print("Synthesizing 'Hello! Welcome to LuMay Insurance.' using OpenAI...")
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input="Hello! Welcome to LuMay Insurance.",
        )
        print("Success! Audio content size:", len(response.content), "bytes")
    except Exception as exc:
        print("Failed:", exc)

if __name__ == "__main__":
    asyncio.run(main())
