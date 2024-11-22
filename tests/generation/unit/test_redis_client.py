import os
import pytest
import redis
import time
import json
import base64

from services.file_management.serviceManager import RedisManager
from services.generation.redis_client import RedisClient
from services.common.Redis_handler import RedisHandler

@pytest.fixture(scope='session')
def redis_handler():
    return RedisHandler()

@pytest.fixture(scope='session')
def redis_client_input():
    redis_host = os.environ.get("redis_host")
    redis_port = os.environ.get("redis_port")
    return redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

@pytest.fixture(scope='session')
def redis_client():
    RedisManager().init()
    return RedisClient()

# Test 1
def test_nonexistent_key(redis_handler, redis_client):
    conversation_block_id = "block999"
    conv_id = "conv999"
    redis_key = f"{conversation_block_id}:{conv_id}"
    output = redis_client.get_query(redis_key)
    assert output == f"No query found in Redis for conversation: {conv_id}"

# Test 2
def test_store_and_retrieve(redis_handler, redis_client):
    conversation_block_id = "block1"
    conv_id = "conv1"
    input_1 = "test content 1"
    redis_key = f"{conversation_block_id}:{conv_id}"
    redis_handler.store_query(conv_id, input_1, conversation_block_id=conversation_block_id)
    assert input_1 == redis_client.get_query(redis_key)

# Test 3
def test_update_existing_key(redis_handler, redis_client):
    conversation_block_id = "block2"
    conv_id = "conv2"
    initial_content = "initial content"
    updated_content = "updated content"
    redis_key = f"{conversation_block_id}:{conv_id}"
    redis_handler.store_query(conv_id, initial_content, conversation_block_id=conversation_block_id)
    redis_handler.store_query(conv_id, updated_content, conversation_block_id=conversation_block_id)
    assert updated_content == redis_client.get_query(redis_key)

# Test 4
def test_delete_key(redis_handler, redis_client):
    conversation_block_id = "block3"
    conv_id = "conv3"
    content = "content to delete"
    redis_key = f"{conversation_block_id}:{conv_id}"
    redis_handler.store_query(conv_id, content, conversation_block_id=conversation_block_id)
    redis_handler.delete_conversation_block(conversation_block_id)
    output = redis_client.get_query(redis_key)
    assert output == f"No query found in Redis for conversation: {conv_id}"

# Test 5
def test_special_characters_key(redis_handler, redis_client):
    conversation_block_id = "block5"
    conv_id = "conv5"
    content = "special content"
    redis_key = f"{conversation_block_id}:{conv_id}"
    redis_handler.store_query(conv_id, content, conversation_block_id=conversation_block_id)
    assert content == redis_client.get_query(redis_key)

# Test 6
def test_key_with_expiration(redis_handler, redis_client):
    conversation_block_id = "block6"
    conv_id = "conv6"
    content = "expiring content"
    redis_key = f"{conversation_block_id}:{conv_id}"
    redis_handler.store_query(conv_id, content, conversation_block_id=conversation_block_id, expiration=1)
    assert redis_client.get_query(redis_key) == content
    time.sleep(2)
    assert redis_client.get_query(redis_key) == f"No query found in Redis for conversation: {conv_id}"

# Test 7
def test_batch_set_and_get(redis_handler, redis_client):
    conversation_block_id = "block7"
    pipeline = redis_handler.client.pipeline()
    
    redis_key_1 = f"{conversation_block_id}:conv7a"
    redis_key_2 = f"{conversation_block_id}:conv7b"
    
    redis_handler.store_query("conv7a", "batch content 1", conversation_block_id=conversation_block_id, pipeline=pipeline)
    redis_handler.store_query("conv7b", "batch content 2", conversation_block_id=conversation_block_id, pipeline=pipeline)
    pipeline.execute()
    
    assert redis_client.get_query(redis_key_1) == "batch content 1"
    assert redis_client.get_query(redis_key_2) == "batch content 2"

# Test 8
def test_store_binary_data(redis_handler, redis_client):
    conversation_block_id = "block8"
    conv_id = "conv8"
    binary_content = b'\x00\xFF\xFE\xFD'
    redis_key = f"{conversation_block_id}:{conv_id}"
    
    redis_handler.store_query(conv_id, binary_content, conversation_block_id=conversation_block_id)
    stored_data = redis_client.get_query(redis_key)
    decoded_data = base64.b64decode(stored_data.encode('utf-8'))
    assert decoded_data == binary_content

# Test 9
def test_increment_numeric_key(redis_handler, redis_client):
    conversation_block_id = "block9"
    conv_id = "conv9"
    redis_key = f"{conversation_block_id}:{conv_id}"
    
    redis_handler.store_query(conv_id, 10, conversation_block_id=conversation_block_id)
    stored_value = redis_client.get_query(redis_key)
    new_value = int(stored_value) + 5
    redis_handler.store_query(conv_id, new_value, conversation_block_id=conversation_block_id)
    assert redis_client.get_query(redis_key) == str(15)

# Test 10
def test_key_exists(redis_handler, redis_client):
    conversation_block_id = "block10"
    conv_id = "conv10"
    
    redis_handler.store_query(conv_id, "some content", conversation_block_id=conversation_block_id)
    assert redis_handler.client.exists(conversation_block_id) == 1
    redis_handler.delete_conversation_block(conversation_block_id)
    assert redis_handler.client.exists(conversation_block_id) == 0

# test 11
def test_get_all_messages(redis_handler, redis_client):
    conversation_block_id = "block11"
    
    # 存储多条消息
    redis_handler.store_query("conv11a", "message 1", conversation_block_id=conversation_block_id)
    redis_handler.store_query("conv11b", "message 2", conversation_block_id=conversation_block_id)
    
    # 获取所有消息
    messages = redis_handler.get_all_messages(conversation_block_id)
    assert len(messages) == 2
    assert messages["conv11a"]["query"] == "message 1"
    assert messages["conv11b"]["query"] == "message 2"