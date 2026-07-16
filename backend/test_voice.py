import asyncio
import httpx

async def test_voice():
    print("Testing Voice Endpoint...")
    async with httpx.AsyncClient() as client:
        # Request token and start session
        res = await client.post("http://localhost:8001/api/v1/voice/start", json={
            "customer_ref": "cust-test",
            "room_name": "test-room"
        }, timeout=30.0)
        print("Status:", res.status_code)
        print("Response:", res.json())

        if res.status_code != 200:
            return
            
        data = res.json().get("data", {})
        session_id = data.get("session_id")
        
        # Wait a few seconds to let Pipecat pipeline spin up
        print("Waiting 5 seconds for Pipecat pipeline to initialize...")
        await asyncio.sleep(5)
        
        # Check session status
        status_res = await client.get(f"http://localhost:8001/api/v1/voice/sessions/{session_id}")
        print("Session Status:", status_res.json())

if __name__ == "__main__":
    asyncio.run(test_voice())
