import re
import os

file_path = 'c:\\projects\\lumay-si-ai-hub\\backend\\.env'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'(?m)^LIVEKIT_URL=.*$', 'LIVEKIT_URL=wss://leo-u5nap7m9.livekit.cloud', content)
content = re.sub(r'(?m)^LIVEKIT_API_KEY=.*$', 'LIVEKIT_API_KEY=APIo6tj7nhCVjpP', content)
content = re.sub(r'(?m)^LIVEKIT_API_SECRET=.*$', 'LIVEKIT_API_SECRET=vbw7K994RHzehYvXUOZZzLZlAufj2swFuDG3LAotHIz', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
