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

    def delete_key(self, key):
        """
        Delete a specific key from Redis.
        
        :param key: The Redis key to delete.
        :return: A message indicating success or failure.
        """
        try:
            # Check if the key exists
            if self.redis_client.exists(key):
                self.redis_client.delete(key)
                return f"Key '{key}' has been deleted."
            else:
                return f"Key '{key}' not found in Redis."
        except Exception as e:
            return f"Error while deleting key '{key}': {str(e)}"


if __name__ == "__main__":
    # Initialize Redis Viewer
    try:
        redis_viewer = RedisViewer()

        while True:
            # Ask the user to choose between viewing or deleting or exiting
            print("\nWhat would you like to do?")
            print("1. View all keys and values")
            print("2. Delete a specific key")
            print("3. Exit")
            choice = input("Enter 1, 2, or 3: ")

            if choice == '1':
                # View all stored key-value pairs
                redis_viewer.view_all_data()

            elif choice == '2':
                # Ask for the key to delete
                key_to_delete = input("Enter the key you want to delete: ")
                delete_message = redis_viewer.delete_key(key_to_delete)
                print(delete_message)

                # Optionally show the remaining keys after deletion
                show_remaining = input("Would you like to see the remaining keys? (y/n): ").lower()
                if show_remaining == 'y':
                    redis_viewer.view_all_data()

            elif choice == '3':
                # Exit the program
                print("Exiting the Redis Viewer. Goodbye!")
                break

            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
