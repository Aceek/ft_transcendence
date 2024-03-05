import asyncio
import uvicorn
import aioredis

async def cleanup_redis():
    print("Nettoyage de Redis...")
    redis = await aioredis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
    await redis.flushall()
    await redis.close()
    print("Nettoyage de Redis terminé.")

if __name__ == "__main__":
    asyncio.run(cleanup_redis())

    uvicorn.run("backend.asgi:application", host="0.0.0.0", port=8000, reload=True)
