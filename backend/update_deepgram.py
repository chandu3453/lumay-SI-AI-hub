import re

file_path = '.env'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update or append
if 'DEEPGRAM_API_KEY' in content:
    content = re.sub(r'(?mi)^DEEPGRAM_API_KEY=.*$', 'DEEPGRAM_API_KEY=342b11de67a02a26846be5098531cf67b0f6e2ee', content)
else:
    content += '\n# Deepgram WebRTC / Audio\nDEEPGRAM_API_KEY=342b11de67a02a26846be5098531cf67b0f6e2ee\n'

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
