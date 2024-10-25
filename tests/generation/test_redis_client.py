import os
import redis
import subprocess

class RedisManager:
    def is_redis_installed(self):
        """Check if Redis is installed"""
        result = subprocess.run(
            ["which", "redis-server"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.returncode == 0

    def is_redis_running(self):
        """Check if Redis server is running"""
        result = subprocess.run(
            ["pgrep", "-f", "redis-server"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.returncode == 0

    def install_redis(self):
        """Install Redis on Linux"""
        if self.is_redis_installed():
            print("Redis is already installed")
        else:
            try:
                # Update packages and install Redis
                subprocess.run(["apt", "update"], check=True)
                subprocess.run(["apt", "install", "-y", "redis-server"], check=True)
                print("Redis has been successfully installed")
            except subprocess.CalledProcessError as e:
                print(f"Error installing Redis: {e}")

    def start_redis(self):
        """Start Redis server on Linux"""
        if self.is_redis_running():
            print("Redis server is already running")
        else:
            try:
                subprocess.run(["redis-server", "--daemonize", "yes"], check=True)
                print("Redis has been successfully started")
            except subprocess.CalledProcessError as e:
                print(f"Error starting Redis: {e}")

    def stop_redis(self):
        """Stop Redis server on Linux"""
        if self.is_redis_running():
            try:
                subprocess.run(["pkill", "-f", "redis-server"], check=True)
                print("Redis has been successfully stopped")
            except subprocess.CalledProcessError as e:
                print(f"Error stopping Redis: {e}")
        else:
            print("Redis server is not running")

    def init(self):
        """Run the full setup process"""
        self.install_redis()
        self.start_redis()

# from services.file_management.serviceManager import RedisManager

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
