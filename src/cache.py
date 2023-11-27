import redis.asyncio as redis
from src.settings import settings

redis_cache = None


async def get_cache():
    global redis_cache

    if redis_cache is None:
        redis_cache = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
    return redis_cache
