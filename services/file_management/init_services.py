import os
import redis
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

def init_redis():
    """
    Initialize and test Redis connection
    """
    
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    
    try:
        logging.info(f"Connecting to Redis at {redis_host}:{redis_port}...")
        redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
        redis_client.ping()
        
        logging.info("Successfully connected to Redis.")
        
        return redis_client
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
        raise e

if __name__ == "__main__":
    try:
        redis_client = init_redis()
    except Exception as e:
        logging.error(f"System failed to start due to: {e}")
