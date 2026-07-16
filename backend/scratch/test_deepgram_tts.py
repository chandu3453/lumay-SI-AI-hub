import os
import asyncio
from dotenv import load_dotenv
import httpx

async def main():
    load_dotenv()
    key = os.getenv("DEEPGRAM_API_KEY")
    print("Deepgram API Key configured:", bool(key), f"({len(key) if key else 0} chars)")
    
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
    headers = {
        "Authorization": f"Token {key}",
        "Content-Type": "application/json"
    }
    json_data = {
        "text": "Hello! Welcome to LuMay Insurance."
    }
    
    try:
        print("Synthesizing using Deepgram API...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=json_data, timeout=10.0)
            print("Status code:", response.status_code)
            if response.status_code == 200:
                print("Success! Audio size:", len(response.content), "bytes")
            else:
                print("Failed. Detail:", response.text)
    except Exception as exc:
        print("Failed:", exc)

if __name__ == "__main__":
    asyncio.run(main())
