import redis
from services.common.config import REDIS_HOST, REDIS_PORT

class RedisClient:
    def __init__(self):
        self.client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

    def get_query(self, conv_id: str) -> str:
        redis_key = conv_id
        try:
            query = self.client.get(redis_key)
            return query if query else f"No query found in Redis for conversation ID: {conv_id}"
        except Exception as e:
            return f"Error while fetching query from Redis: {str(e)}"
