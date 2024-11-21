import pytest
from unittest.mock import patch, MagicMock
from services.generation.llm_handler import LLMHandler  # Correct module path

@pytest.fixture
def mock_chat_openai():
    with patch('services.generation.llm_handler.ChatOpenAI') as MockChatOpenAI:
        mock_llm = MockChatOpenAI.return_value
        yield mock_llm

def test_generate_answer(mock_chat_openai):
    # Arrange
    handler = LLMHandler('RAG')
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
    handler = LLMHandler('RAG')
    mock_chat_openai.invoke.return_value.content = "Answer for empty question"
    
    context = "Some context information"
    question = ""
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for empty question"

def test_generate_answer_empty_context(mock_chat_openai):
    # Test with an empty context
    handler = LLMHandler('RAG')
    mock_chat_openai.invoke.return_value.content = "Answer for empty context"

    context = ""
    question = "What is the context?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for empty context"

def test_generate_answer_long_context(mock_chat_openai):
    # Test with a very long context
    handler = LLMHandler('RAG')
    mock_chat_openai.invoke.return_value.content = "Answer for long context"
    
    context = "This is a very long context" * 100  # Long string for context
    question = "What is the context?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for long context"

def test_generate_answer_long_question(mock_chat_openai):
    # Test with a very long question
    handler = LLMHandler('RAG')
    mock_chat_openai.invoke.return_value.content = "Answer for long question"
    
    context = "Some context information"
    question = "What is the meaning of life?" * 100  # Long string for question
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for long question"

def test_generate_answer_special_characters(mock_chat_openai):
    # Test with special characters in context and question
    handler = LLMHandler('RAG')
    mock_chat_openai.invoke.return_value.content = "Answer for special characters"
    
    context = "Context with special characters: @#$%^&*()!"
    question = "What about special characters?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for special characters"

def test_generate_answer_numeric_context(mock_chat_openai):
    # Test with numeric values in the context
    handler = LLMHandler('RAG')
    mock_chat_openai.invoke.return_value.content = "Answer for numeric context"
    
    context = "1234567890"
    question = "What is the number?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for numeric context"

def test_generate_answer_numeric_question(mock_chat_openai):
    # Test with numeric values in the question
    handler = LLMHandler('RAG')
    mock_chat_openai.invoke.return_value.content = "Answer for numeric question"
    
    context = "Some context information"
    question = "What is 1234567890?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for numeric question"

def test_generate_answer_mixed_context_and_question(mock_chat_openai):
    # Test with mixed types (numbers, special characters, and letters)
    handler = LLMHandler('RAG')
    mock_chat_openai.invoke.return_value.content = "Answer for mixed input"
    
    context = "Mix of numbers 123, special chars @#&, and letters."
    question = "What is the mix?"
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for mixed input"

def test_generate_answer_invalid_input(mock_chat_openai):
    # Test with invalid or unusual inputs (empty context and empty question)
    handler = LLMHandler('RAG')
    mock_chat_openai.invoke.return_value.content = "Answer for invalid input"
    
    context = ""
    question = ""
    result = handler.generate_answer(context = context, question = question)
    filled_prompt = handler.prompt.format(context=context, question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for invalid input"

def test_generate_answer_gpt_mode(mock_chat_openai):
    # Test GPT mode with a basic question
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer from GPT mode"

    question = "What is the meaning of life?"
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer from GPT mode"

def test_generate_answer_gpt_mode_empty_question(mock_chat_openai):
    # Test GPT mode with an empty question
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer for empty question in GPT mode"

    question = ""
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for empty question in GPT mode"

def test_generate_answer_gpt_mode_special_characters(mock_chat_openai):
    # Test GPT mode with special characters in the question
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer for special characters in GPT mode"

    question = "What about special characters like @#$%^&*()?"
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for special characters in GPT mode"

def test_generate_answer_gpt_mode_numeric_question(mock_chat_openai):
    # Test GPT mode with numeric values in the question
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer for numeric question in GPT mode"

    question = "What is 1234567890?"
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for numeric question in GPT mode"

def test_generate_answer_gpt_mode_basic_question(mock_chat_openai):
    # Test GPT mode with a basic question
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer from GPT mode"

    question = "What is the meaning of life?"
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer from GPT mode"

def test_generate_answer_gpt_mode_long_question(mock_chat_openai):
    # Test GPT mode with a very long question
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer for long question in GPT mode"

    question = "What is the meaning of life?" * 100  # Long string for question
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for long question in GPT mode"

def test_generate_answer_gpt_mode_mixed_input(mock_chat_openai):
    # Test GPT mode with mixed types (numbers, special characters, and letters)
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer for mixed input in GPT mode"

    question = "Mix of numbers 123, special chars @#&, and letters."
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for mixed input in GPT mode"

def test_generate_answer_gpt_mode_unicode_characters(mock_chat_openai):
    # Test GPT mode with Unicode characters in the question
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer for Unicode characters in GPT mode"

    question = "What about Unicode characters like 😊, 你好, and مرحبا?"
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for Unicode characters in GPT mode"

def test_generate_answer_gpt_mode_edge_case_question(mock_chat_openai):
    # Test GPT mode with an edge case question
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer for edge case question in GPT mode"

    question = "What is the airspeed velocity of an unladen swallow?"
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for edge case question in GPT mode"

def test_generate_answer_gpt_mode_html_content(mock_chat_openai):
    # Test GPT mode with HTML content in the question
    handler = LLMHandler(mode='GPT')
    mock_chat_openai.invoke.return_value.content = "Answer for HTML content in GPT mode"

    question = "<p>What is the meaning of <strong>life</strong>?</p>"
    result = handler.generate_answer(question=question)

    filled_prompt = handler.prompt.format(question=question)
    mock_chat_openai.invoke.assert_called_once_with(filled_prompt)
    assert result == "Answer for HTML content in GPT mode"