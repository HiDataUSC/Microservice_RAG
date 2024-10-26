import pytest
import redis
from services.common.config import REDIS_HOST, REDIS_PORT

from services.file_management.serviceManager import RedisManager
from services.generation.redis_client import RedisClient

# Initialize RedisManager to ensure Redis setup
RedisManager().init()  # Starts Redis if not already running
redis_client = RedisClient()
redis_client_input = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

# Connect to Redis and test storage and retrieval

def test_nonexistent_key():
    nonexistent_id = 999
    output = redis_client.get_query(nonexistent_id)
    assert output == f"No query found in Redis for conversation ID: {nonexistent_id}"

def test_store_and_retrieve():
    text_id_1 = 1
    input_1 = "test content 1"
    redis_client_input.set(f"query:{text_id_1}", input_1)

    assert input_1 == redis_client.get_query(text_id_1)

def test_update_existing_key():
    text_id = 2
    initial_content = "initial content"
    updated_content = "updated content"
    redis_client_input.set(f"query:{text_id}", initial_content)
    redis_client_input.set(f"query:{text_id}", updated_content)
    assert updated_content == redis_client.get_query(text_id)

def test_delete_key():
    text_id = 3
    content = "content to delete"
    redis_client_input.set(f"query:{text_id}", content)
    redis_client_input.delete(f"query:{text_id}")
    output = redis_client.get_query(text_id)
    assert output == f"No query found in Redis for conversation ID: {text_id}"

def test_special_characters_key():
    text_id = "special!@#$%^&*()_+"
    content = "special content"
    redis_client_input.set(f"query:{text_id}", content)
    assert content == redis_client.get_query(text_id)