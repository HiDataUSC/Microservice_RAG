import pytest
from unittest.mock import patch, MagicMock
from services.generation.llm_handler import LLMHandler  # Correct module path

@pytest.fixture
def mock_chat_openai():
    with patch('services.generation.llm_handler.ChatOpenAI') as MockChatOpenAI:
        mock_llm = MockChatOpenAI.return_value
        yield mock_llm

@pytest.fixture(scope='module')
def llm_handler():
    return LLMHandler()

def test_generate_answer(mock_chat_openai):
    # Arrange
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for context information"

    context = "The context information"
    question = "What is the context?"

    # Act
    result = handler.generate_answer(context = context, question = question)

    # Assert
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for context information"

def test_generate_answer_empty_question(mock_chat_openai):
    # Test with an empty question
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for empty question"
    
    context = "Some context information"
    question = ""
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for empty question"

def test_generate_answer_empty_context(mock_chat_openai):
    # Test with an empty context
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for empty context"

    context = ""
    question = "What is the context?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for empty context"

def test_generate_answer_long_context(mock_chat_openai):
    # Test with a very long context
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for long context"
    
    context = "This is a very long context" * 100  # Long string for context
    question = "What is the context?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for long context"

def test_generate_answer_long_question(mock_chat_openai):
    # Test with a very long question
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for long question"
    
    context = "Some context information"
    question = "What is the meaning of life?" * 100  # Long string for question
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for long question"

def test_generate_answer_special_characters(mock_chat_openai):
    # Test with special characters in context and question
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for special characters"
    
    context = "Context with special characters: @#$%^&*()!"
    question = "What about special characters?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for special characters"

def test_generate_answer_numeric_context(mock_chat_openai):
    # Test with numeric values in the context
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for numeric context"
    
    context = "1234567890"
    question = "What is the number?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for numeric context"

def test_generate_answer_numeric_question(mock_chat_openai):
    # Test with numeric values in the question
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for numeric question"
    
    context = "Some context information"
    question = "What is 1234567890?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for numeric question"

def test_generate_answer_mixed_context_and_question(mock_chat_openai):
    # Test with mixed types (numbers, special characters, and letters)
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for mixed input"
    
    context = "Mix of numbers 123, special chars @#&, and letters."
    question = "What is the mix?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for mixed input"

def test_generate_answer_invalid_input(mock_chat_openai):
    # Test with invalid or unusual inputs (empty context and empty question)
    handler = LLMHandler()
    mock_chat_openai.invoke.return_value.content = "Answer for invalid input"
    
    context = ""
    question = ""
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for invalid input"
