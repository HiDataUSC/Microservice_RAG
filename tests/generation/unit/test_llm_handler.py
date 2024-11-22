import pytest
from unittest.mock import patch, MagicMock, ANY
from services.generation.llm_handler import LLMHandler

class ParamMatcher:
    """Custom parameter matcher for testing"""
    def __init__(self, **required_params):
        self.required_params = required_params

    def __eq__(self, other):
        if not isinstance(other, str):
            return False
        # Check if all required parameters are in the prompt string
        return all(
            str(value) in other
            for value in self.required_params.values()
        )

@pytest.fixture
def mock_chat_openai():
    with patch('services.generation.llm_handler.ChatOpenAI') as MockChatOpenAI:
        mock_llm = MockChatOpenAI.return_value
        mock_llm.invoke.return_value.content = "Mocked answer"
        yield mock_llm

class TestLLMHandler:
    """Test cases for LLMHandler"""
    
    @pytest.fixture(autouse=True)
    def setup(self, mock_chat_openai):
        self.mock_llm = mock_chat_openai
        
    def verify_llm_call(self, handler, expected_params):
        """Helper method to verify LLM calls"""
        # Create parameter matcher
        matcher = ParamMatcher(**expected_params)
        
        # Verify the call
        self.mock_llm.invoke.assert_called_once()
        actual_prompt = self.mock_llm.invoke.call_args[0][0]
        assert matcher == actual_prompt
        
    def test_rag_mode_basic(self):
        """Test RAG mode with basic parameters"""
        handler = LLMHandler('RAG')
        params = {
            'question': "Test question",
            'context': "Test context"
        }
        
        result = handler.generate_answer(**params)
        
        self.verify_llm_call(handler, params)
        assert result == "Mocked answer"

    def test_gpt_mode_basic(self):
        """Test GPT mode with basic parameters"""
        handler = LLMHandler('GPT')
        params = {
            'question': "Test question"
        }
        
        result = handler.generate_answer(**params)
        
        self.verify_llm_call(handler, params)
        assert result == "Mocked answer"

    @pytest.mark.parametrize("test_input", [
        {'question': ""},  # Empty question
        {'question': "Test" * 100},  # Long question
        {'question': "Special chars: @#$%"},  # Special characters
        {'question': "1234567890"},  # Numbers
        {'question': "😊 你好"},  # Unicode
        {'question': "<p>HTML</p>"}  # HTML
    ])
    def test_input_variations(self, test_input):
        """Test various input types"""
        handler = LLMHandler('RAG')
        result = handler.generate_answer(**test_input)
        
        self.verify_llm_call(handler, test_input)
        assert result == "Mocked answer"

    def test_with_optional_params(self):
        """Test with additional optional parameters"""
        handler = LLMHandler('RAG')
        params = {
            'question': "Test question",
            'context': "Test context",
            'chat_history': "Test history",
            'new_param': "Should not break test"  # 新参数不会影响测试
        }
        
        result = handler.generate_answer(**params)
        
        # 只验证必要参数
        essential_params = {
            'question': params['question'],
            'context': params['context']
        }
        self.verify_llm_call(handler, essential_params)
        assert result == "Mocked answer"

    @pytest.mark.parametrize("mode", ['RAG', 'GPT'])
    def test_different_modes(self, mode):
        """Test both RAG and GPT modes"""
        handler = LLMHandler(mode)
        params = {'question': "Test question"}
        
        result = handler.generate_answer(**params)
        
        self.verify_llm_call(handler, params)
        assert result == "Mocked answer"