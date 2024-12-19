import pytest
from unittest.mock import MagicMock
from services.Text_Generation.app import Generation

class TestHelper:
    """Helper class for testing"""
    @staticmethod
    def create_redis_key(block_id: str, conv_id: str) -> str:
        return f"{block_id}:{conv_id}"
        
    @staticmethod
    def verify_llm_call(mock_generation, expected_params):
        """Verify LLM call with flexible parameter matching"""
        actual_args = mock_generation.llm_handler.generate_answer.call_args.kwargs
        for key, value in expected_params.items():
            assert key in actual_args
            assert value in str(actual_args[key])

class TestGeneration:
    """Integration tests for Generation class"""
    
    @pytest.fixture
    def base_params(self):
        """Common test parameters"""
        return {
            'conv_id': "12345",
            'conversation_block_id': "block123",
            'directory_path': "/fake/path"
        }

    @pytest.fixture
    def mock_RAG_generation(self):
        generation = Generation('RAG')
        generation.redis_client.get_query = MagicMock(return_value="What is the meaning of life?")
        generation.file_reader.read_files = MagicMock(return_value="The meaning of life is to give life a meaning.")
        generation.llm_handler.generate_answer = MagicMock(return_value="The meaning of life is 42.")
        return generation

    @pytest.fixture
    def mock_GPT_generation(self):
        generation = Generation('GPT')
        generation.redis_client.get_query = MagicMock(return_value="What is the meaning of life?")
        generation.llm_handler.generate_answer = MagicMock(return_value="The meaning of life is 42.")
        return generation

    @pytest.mark.parametrize("test_case", [
        {
            'name': "basic_rag",
            'mode': 'RAG',
            'query': "What is the meaning of life?",
            'context': "The meaning of life is to give life a meaning.",
            'expected_answer': "The meaning of life is 42."
        },
        {
            'name': "empty_context",
            'mode': 'RAG',
            'query': "What is the meaning of life?",
            'context': "",
            'expected_result': "No relevant documents found in the directory to answer the question."
        },
        {
            'name': "unicode_chars",
            'mode': 'RAG',
            'query': "What about Unicode characters like 😊, 你好?",
            'context': "Some context",
            'expected_answer': "The meaning of life is 42."
        }
    ])
    def test_rag_scenarios(self, mock_RAG_generation, base_params, test_case):
        """Test various RAG scenarios"""
        # Setup mocks based on test case
        mock_RAG_generation.redis_client.get_query = MagicMock(return_value=test_case['query'])
        mock_RAG_generation.file_reader.read_files = MagicMock(return_value=test_case['context'])
        
        # Execute test
        redis_key = TestHelper.create_redis_key(
            base_params['conversation_block_id'], 
            base_params['conv_id']
        )
        result = mock_RAG_generation.generate_answer(redis_key, base_params['directory_path'])
        
        # Verify results
        if 'expected_result' in test_case:
            assert result == test_case['expected_result']
        else:
            expected_params = {
                'question': test_case['query']
            }
            if test_case['context']:
                expected_params['context'] = test_case['context']
                
            TestHelper.verify_llm_call(mock_RAG_generation, expected_params)
            assert result == test_case['expected_answer']

    @pytest.mark.parametrize("test_case", [
        {
            'name': "basic_gpt",
            'query': "What is the meaning of life?",
            'expected_answer': "The meaning of life is 42."
        },
        {
            'name': "empty_query",
            'query': "",
            'expected_answer': "The meaning of life is 42."
        },
        {
            'name': "special_chars",
            'query': "What about special characters like @#$%^&*()?",
            'expected_answer': "The meaning of life is 42."
        }
    ])
    def test_gpt_scenarios(self, mock_GPT_generation, base_params, test_case):
        """Test various GPT scenarios"""
        # Setup mock
        mock_GPT_generation.redis_client.get_query = MagicMock(return_value=test_case['query'])
        
        # Execute test
        redis_key = TestHelper.create_redis_key(
            base_params['conversation_block_id'], 
            base_params['conv_id']
        )
        result = mock_GPT_generation.generate_answer(redis_key, base_params['directory_path'])
        
        # Verify results
        TestHelper.verify_llm_call(mock_GPT_generation, {'question': test_case['query']})
        assert result == test_case['expected_answer']

    def test_redis_error_handling(self, mock_RAG_generation, base_params):
        """Test Redis error handling"""
        mock_RAG_generation.redis_client.get_query = MagicMock(
            side_effect=Exception("Redis connection error")
        )
        
        redis_key = TestHelper.create_redis_key(
            base_params['conversation_block_id'], 
            base_params['conv_id']
        )
        result = mock_RAG_generation.generate_answer(redis_key, base_params['directory_path'])
        
        assert "Redis error" in str(mock_RAG_generation.llm_handler.generate_answer.call_args)
        assert result == "The meaning of life is 42."
