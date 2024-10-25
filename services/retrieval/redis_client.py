import redis
from services.common.config import REDIS_HOST, REDIS_PORT

class RedisHandler:
    def __init__(self):
        self.client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

    def store_query(self, query):
        query_id = -1 
        self.client.set(f'query:{query_id}', query)
        return query_id
