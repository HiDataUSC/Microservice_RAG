import os
import pytest
import redis
import time

from services.file_management.serviceManager import RedisManager
from services.generation.redis_client import RedisClient

@pytest.fixture(scope='session')
def redis_client_input():
    redis_host = os.environ.get("redis_host")
    redis_port = os.environ.get("redis_port")
    
    return redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

# Initialize RedisManager to ensure Redis setup
@pytest.fixture(scope='session')
def redis_client():
    RedisManager().init()
    return RedisClient()

# Test 1: It verifies that querying a non-existent key (in this case, 999) should return an appropriate "No query found" message.
def test_nonexistent_key(redis_client_input, redis_client):
    nonexistent_id = 999
    output = redis_client.get_query(nonexistent_id)
    assert output == f"No query found in Redis for conversation ID: {nonexistent_id}"

# Test 2: It stores data in Redis and checks if it can successfully retrieve the same data.
def test_store_and_retrieve(redis_client_input, redis_client):
    text_id_1 = 1
    input_1 = "test content 1"
    redis_client_input.set(text_id_1, input_1)

    assert input_1 == redis_client.get_query(text_id_1)

# Test 3: tests updating the value of an existing key. After updating the key, it verifies that the new value is retrieved.
def test_update_existing_key(redis_client_input, redis_client):
    text_id = 2
    initial_content = "initial content"
    updated_content = "updated content"
    redis_client_input.set(text_id, initial_content)
    redis_client_input.set(text_id, updated_content)
    assert updated_content == redis_client.get_query(text_id)

# Test 4:   hecks if the appropriate "No query found" message is returned.
def test_delete_key(redis_client_input, redis_client):
    text_id = 3
    content = "content to delete"
    redis_client_input.set(text_id, content)
    redis_client_input.delete(text_id)
    output = redis_client.get_query(text_id)
    assert output == f"No query found in Redis for conversation ID: {text_id}"

# Test 5: This test checks if Redis can handle keys with special characters.
def test_special_characters_key(redis_client_input, redis_client):
    text_id = "special!@#$%^&*()_+"
    content = "special content"
    redis_client_input.set(text_id, content)
    assert content == redis_client.get_query(text_id)

# Test 6: Test key with expiration
def test_key_with_expiration(redis_client_input, redis_client):
    text_id = 6
    content = "expiring content"
    redis_client_input.setex(text_id, 1, content)  # Key expires in 1 second
    assert redis_client.get_query(text_id) == content
    time.sleep(2)  # Sleep to allow expiration
    assert redis_client.get_query(text_id) == f"No query found in Redis for conversation ID: {text_id}"

# Test 7: Test batch set and get using pipeline
def test_batch_set_and_get(redis_client_input, redis_client):
    pipeline = redis_client_input.pipeline()
    pipeline.set(5, "batch content 1")
    pipeline.set(6, "batch content 2")
    pipeline.execute()

    assert redis_client.get_query(5) == "batch content 1"
    assert redis_client.get_query(6) == "batch content 2"

# Test 8: Test binary data
def test_store_binary_data(redis_client_input, redis_client):
    # 禁用 decode_responses，确保 Redis 返回原始二进制数据
    redis_host = os.environ.get("redis_host")
    redis_port = os.environ.get("redis_port")
    redis_client_input = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=False)
    text_id = 8
    binary_content = b'\x00\xFF\xFE\xFD'  # 一些二进制数据
    redis_client_input.set(text_id, binary_content)
    assert redis_client_input.get(text_id) == binary_content

# Test 9: Test incrementing a numeric key
def test_increment_numeric_key(redis_client_input, redis_client):
    text_id = 9
    redis_client_input.set(text_id, 10)  # Start at 10
    redis_client_input.incr(text_id, 5)  # Increment by 5
    assert redis_client.get_query(text_id) == "15"

# Test 10: Test key existence
def test_key_exists(redis_client_input, redis_client):
    text_id = 10
    redis_client_input.set(text_id, "some content")
    assert redis_client_input.exists(text_id) == 1  # Key exists
    redis_client_input.delete(text_id)
    assert redis_client_input.exists(text_id) == 0  # Key does not exist