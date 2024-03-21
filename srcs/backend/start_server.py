import asyncio
import uvicorn
import aioredis
import subprocess
from logging.config import dictConfig
from logging_config import log_config 

async def cleanup_redis():
    print("Nettoyage de Redis...")
    redis = await aioredis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
    await redis.flushall()
    await redis.close()
    print("Nettoyage de Redis terminé.")

def run_migrations():
    print("Applying database migrations...")
    subprocess.run(["python3", "manage.py", "migrate"], check=True)
    print("Database migrations applied.")

if __name__ == "__main__":
    asyncio.run(cleanup_redis())

    run_migrations()

    dictConfig(log_config)

    uvicorn.run("backend.asgi:application", host="0.0.0.0", port=8000, reload=True, log_config=log_config)
