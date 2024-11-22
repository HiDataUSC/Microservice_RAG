import os
import pytest
import redis
import time
from typing import Dict, Any, Union
from services.file_management.serviceManager import RedisManager
from services.generation.redis_client import RedisClient
from services.common.Redis_handler import RedisHandler

class RedisTestHelper:
    """Helper class for Redis testing"""
    @staticmethod
    def create_key(block_id: str, conv_id: str) -> str:
        return f"{block_id}:{conv_id}"
    
    @staticmethod
    def verify_message(actual: Union[str, Dict], expected_content: str) -> bool:
        """Verify message content regardless of format changes"""
        if isinstance(actual, dict):
            return expected_content in actual.get('content', '')
        if isinstance(actual, str):
            try:
                # Try to parse as dict string
                import ast
                parsed = ast.literal_eval(actual)
                return expected_content in parsed.get('content', '')
            except:
                return expected_content in actual
        return False

    @staticmethod
    def extract_message_content(message: Union[str, Dict]) -> str:
        """Extract content from message regardless of format"""
        if isinstance(message, dict):
            return message.get('content', '')
        if isinstance(message, str):
            try:
                parsed = ast.literal_eval(message)
                return parsed.get('content', '')
            except:
                return message
        return ''

class TestRedisClient:
    """Test cases for Redis client operations"""
    
    @pytest.fixture(scope='class')
    def redis_handler(self):
        return RedisHandler()

    @pytest.fixture(scope='class')
    def redis_client(self):
        RedisManager().init()
        return RedisClient()
        
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, redis_handler):
        """Setup and teardown for each test"""
        self.test_blocks = []
        yield
        # Cleanup after each test
        for block_id in self.test_blocks:
            redis_handler.delete_conversation_block(block_id)

    def store_test_message(self, redis_handler, block_id: str, conv_id: str, 
                          content: Any, **kwargs) -> str:
        """Helper method to store test messages"""
        self.test_blocks.append(block_id)
        redis_key = RedisTestHelper.create_key(block_id, conv_id)
        redis_handler.store_query(conv_id, content, conversation_block_id=block_id, **kwargs)
        return redis_key

    @pytest.mark.parametrize("test_data", [
        {"content": "simple text"},
        {"content": "特殊字符 @#$%"},
        {"content": "😊 emoji test"},
        {"content": "Multi\nLine\nText"},
        {"content": "HTML <p>test</p>"},
        {"content": " " * 1000},  # Large content
        {"content": ""}  # Empty content
    ])
    def test_store_and_retrieve_variations(self, redis_handler, redis_client, test_data):
        """Test storing and retrieving various types of content"""
        block_id = f"test_block_{hash(test_data['content'])}"
        conv_id = "test_conv"
        redis_key = self.store_test_message(redis_handler, block_id, conv_id, test_data['content'])
        
        result = redis_client.get_query(redis_key)
        content = RedisTestHelper.extract_message_content(result)
        assert test_data['content'] in content

    def test_conversation_history(self, redis_handler, redis_client):
        """Test conversation history functionality"""
        block_id = "history_test"
        self.test_blocks.append(block_id)
        
        # Store multiple messages
        messages = [
            ("conv1", "message 1"),
            ("conv2", "message 2"),
            ("conv3", "message 3")
        ]
        
        for conv_id, content in messages:
            redis_handler.store_query(conv_id, content, conversation_block_id=block_id)
            
        # Verify history
        history = redis_handler.get_conversation_history(block_id)
        assert len(history) == len(messages)
        
        # Get all message contents from history
        history_contents = [
            RedisTestHelper.extract_message_content(msg)
            for msg in history
        ]
        
        # Verify all expected messages are present
        expected_contents = [content for _, content in messages]
        assert all(
            any(expected in actual for actual in history_contents)
            for expected in expected_contents
        )

    @pytest.mark.parametrize("expiration", [1, 2, 3])
    def test_expiration_scenarios(self, redis_handler, redis_client, expiration):
        """Test different expiration scenarios"""
        block_id = f"expiration_test_{expiration}"
        conv_id = "test_conv"
        content = "expiring content"
        
        redis_key = self.store_test_message(
            redis_handler, block_id, conv_id, content, 
            expiration=expiration
        )
        
        # Verify content exists
        assert RedisTestHelper.verify_message(
            redis_client.get_query(redis_key), 
            content
        )
        
        # Wait for expiration
        time.sleep(expiration + 1)
        
        # Verify content expired
        result = redis_client.get_query(redis_key)
        assert "No query found" in result

    def test_batch_operations(self, redis_handler, redis_client):
        """Test batch operations with pipeline"""
        block_id = "batch_test"
        self.test_blocks.append(block_id)
        
        with redis_handler.client.pipeline() as pipe:
            for i in range(5):
                redis_handler.store_query(
                    f"conv{i}", 
                    f"content{i}", 
                    conversation_block_id=block_id,
                    pipeline=pipe
                )
            pipe.execute()
        
        # Verify all messages
        for i in range(5):
            redis_key = RedisTestHelper.create_key(block_id, f"conv{i}")
            result = redis_client.get_query(redis_key)
            assert RedisTestHelper.verify_message(result, f"content{i}")