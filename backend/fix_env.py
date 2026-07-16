import re

with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

# Clean up broken stuff
content = re.sub(r'# ── Redis ──.*?APP_REDIS_HOST=10\.1\.3\.26', '', content, flags=re.DOTALL)
content = re.sub(r'DATABASE__ECHO=false\s*', '', content)
content = re.sub(r'APP_DB_ECHO=true\s*', 'APP_DB_ECHO=true\n', content)

block = """
DATABASE__URL=sqlite+aiosqlite:///./lumay_dev.db?timeout=30
DATABASE__POOL_SIZE=5
DATABASE__MAX_OVERFLOW=10
DATABASE__ECHO=false

# ── Redis ──────────────────────────────────────────────────────
APP_REDIS_HOST=localhost
APP_REDIS_PORT=6379
APP_REDIS_DB=0
REDIS__URL=redis://localhost:6379/0
REDIS__MAX_CONNECTIONS=50

# ── RabbitMQ ───────────────────────────────────────────────────
APP_RABBITMQ_HOST=localhost
APP_RABBITMQ_PORT=5672
APP_RABBITMQ_USER=user
APP_RABBITMQ_PASSWORD=YOS"GcUo2"21
APP_RABBITMQ_QUEUE_NAME=dev_voice_agent_queue
RABBITMQ__URL=amqp://user:YOS%22GcUo2%2221@localhost:5672/

# ── Auth / JWT ─────────────────────────────────────────────────
JWT__SECRET_KEY=uujuVghVlquMzo1bIa72A3x1lMT5BQ0E
JWT__ALGORITHM=HS256
JWT__ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT__REFRESH_TOKEN_EXPIRE_DAYS=7

# ── CORS ───────────────────────────────────────────────────────
CORS__ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"]
CORS__ALLOW_CREDENTIALS=true
"""

if '# ── Logging ──' in content:
    content = content.replace('# ── Logging ──', block + '\n# ── Logging ──')
else:
    content += '\n' + block

with open('.env', 'w', encoding='utf-8') as f:
    f.write(content)
