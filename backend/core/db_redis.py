import redis

REDIS_URL = "redis://redis-db:6379/0"

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client
