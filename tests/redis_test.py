import redis
import os

# Load Redis configuration from environment variables
redis_host = os.getenv('REDIS_HOST', 'localhost')  # 默认使用localhost
redis_port = os.getenv('REDIS_PORT', 6379)         # 默认Redis端口为6379

# Connect to Redis
redis_client = redis.StrictRedis(host=redis_host, port=int(redis_port), db=0)

def store_text_in_redis(text_id, text_content):
    """
    Function to store a text content into Redis.
    """
    try:
        # Store the text content in Redis
        redis_client.set(text_id, text_content)
        print(f"Successfully stored text with ID '{text_id}' in Redis.")
        
        # Retrieve the text content from Redis
        stored_text_content = redis_client.get(text_id)
        
        if stored_text_content:
            print(f"Successfully retrieved content for text ID '{text_id}' from Redis:")
            print(stored_text_content.decode('utf-8'))  # Decode from bytes to string
        else:
            print(f"Failed to retrieve content for text ID '{text_id}' from Redis.")
    except Exception as e:
        print(f"An error occurred while working with Redis: {e}")

if __name__ == "__main__":
    # Define a text ID and the text content you want to store
    text_id = "sample_text_001"
    text_content = "This is a sample text content that will be stored in Redis."
    
    # Store and retrieve the text content from Redis
    store_text_in_redis(text_id, text_content)
