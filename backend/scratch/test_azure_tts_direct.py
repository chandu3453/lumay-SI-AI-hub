import os
import asyncio
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

async def main():
    load_dotenv()
    key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")
    endpoint = os.getenv("AZURE_TTS_ENDPOINT")
    
    print("Azure Speech Key configured:", bool(key))
    print("Azure Speech Region:", region)
    print("Azure TTS Endpoint:", endpoint)
    
    # Use endpoint instead of region to avoid 401 on custom domain!
    speech_config = speechsdk.SpeechConfig(subscription=key, endpoint=endpoint)
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    
    print("Synthesizing 'Hello! Welcome to LuMay Insurance.'...")
    result = synthesizer.speak_text_async("Hello! Welcome to LuMay Insurance.").get()
    
    print("Result reason:", result.reason)
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Success! Audio data size:", len(result.audio_data), "bytes")
    else:
        print("Failed. Cancellation details:", result.cancellation_details if hasattr(result, "cancellation_details") else "None")
        if hasattr(result, "cancellation_details"):
            print("Error code:", result.cancellation_details.error_code)
            print("Error details:", result.cancellation_details.error_details)

if __name__ == "__main__":
    asyncio.run(main())
