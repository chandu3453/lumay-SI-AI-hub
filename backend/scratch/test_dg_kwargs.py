import os
from dotenv import load_dotenv
from pipecat.services.deepgram.stt import DeepgramSTTService

load_dotenv()
dg_key = os.getenv("DEEPGRAM_API_KEY", "")
stt = DeepgramSTTService(
    api_key=dg_key,
    settings=DeepgramSTTService.Settings(
        endpointing=1500,
        utterance_end_ms=1500
    )
)

kwargs = stt._build_connect_kwargs()
print("Generated Connect Kwargs:")
for k, v in kwargs.items():
    print(f"  {k}: {v} (type: {type(v).__name__})")
