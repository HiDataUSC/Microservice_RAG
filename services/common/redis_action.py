import redis

class RedisViewer:
    """Class to interact with Redis and view stored content."""
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        """Initialize the RedisViewer with Redis connection settings."""
        try:
            self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
            # Check if Redis server is running by sending a PING command
            if self.redis_client.ping():
                print(f"Connected to Redis server at {redis_host}:{redis_port}")
        except redis.ConnectionError as e:
            print(f"Error: Unable to connect to Redis server at {redis_host}:{redis_port}.")
            print(f"Details: {e}")
            self.redis_client = None  # Set redis_client to None to prevent further operations

    def get_all_keys(self):
        """
        Retrieve all keys from the Redis database.
        
        :return: List of all keys stored in Redis.
        """
        return self.redis_client.keys()

    def get_value_for_key(self, key):
        """
        Retrieve the value for a given key from Redis.
        
        :param key: The Redis key for which to retrieve the value.
        :return: The value associated with the provided key.
        """
        return self.redis_client.get(key)

    def view_all_data(self):
        """
        Retrieve and display all key-value pairs stored in Redis.
        """
        keys = self.get_all_keys()
        if not keys:
            print("No keys found in Redis.")
            return
        
        for key in keys:
            value = self.get_value_for_key(key)
            print(f"Key: {key} -> Value: {value}")


if __name__ == "__main__":
    # Initialize Redis Viewer
    try:
        redis_viewer = RedisViewer()
        # View all stored key-value pairs
        redis_viewer.view_all_data()
    except Exception:
        pass
        
