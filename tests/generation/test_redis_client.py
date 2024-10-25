import os
import redis

from services.file_management.serviceManager import RedisManager

# Configure Redis connection settings (localhost because we're using Docker)
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'

# Initialize RedisManager to ensure Redis setup
redis_manager = RedisManager()
redis_manager.init()  # Starts Redis if not already running

# Connect to Redis and test storage and retrieval
redis_client = redis.StrictRedis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), db=0)

def store_and_retrieve_test():
    # Test data
    text_id = "test_key"
    text_content = "This is a test value"

    # Store the test data in Redis
    redis_client.set(text_id, text_content)
    print(f"Stored {text_id}: '{text_content}' in Redis.")

    # Retrieve and verify the test data
    retrieved_content = redis_client.get(text_id).decode('utf-8')
    print(f"Retrieved {text_id}: '{retrieved_content}' from Redis.")

    assert retrieved_content == text_content, "The retrieved content does not match the stored content!"

if __name__ == "__main__":
    store_and_retrieve_test()
    print("Test completed successfully.")
