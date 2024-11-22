import pytest
from unittest.mock import MagicMock
from services.generation.app import Generation

@pytest.fixture
def mock_RAG_generation():
    # Create a Generation instance with mocked dependencies
    generation = Generation('RAG')

    # Mock RedisClient behavior
    generation.redis_client.get_query = MagicMock(return_value="What is the meaning of life?")

    # Mock FileReader behavior
    generation.file_reader.read_files = MagicMock(return_value="The meaning of life is to give life a meaning.")

    # Mock LLMHandler behavior
    generation.llm_handler.generate_answer = MagicMock(return_value="The meaning of life is 42.")

    return generation

@pytest.fixture
def mock_GPT_generation():
    # Create a Generation instance with mocked dependencies
    generation = Generation('GPT')

    # Mock RedisClient behavior
    generation.redis_client.get_query = MagicMock(return_value="What is the meaning of life?")

    # Mock FileReader behavior
    generation.file_reader.read_files = MagicMock(return_value="The meaning of life is to give life a meaning.")

    # Mock LLMHandler behavior
    generation.llm_handler.generate_answer = MagicMock(return_value="The meaning of life is 42.")

    return generation

# Test 1: Verify normal operation with valid query and context
def test_generate_answer(mock_RAG_generation):
    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_RAG_generation.file_reader.read_files.assert_called_once_with(directory_path)
    mock_RAG_generation.llm_handler.generate_answer.assert_called_once_with(
        question="What is the meaning of life?",
        context="The meaning of life is to give life a meaning."
    )
    assert result == "The meaning of life is 42."

# Test 2: Handling empty context (empty directory)
def test_generate_answer_no_context(mock_RAG_generation):
    mock_RAG_generation.file_reader.read_files = MagicMock(return_value="")
    
    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    assert result == "No relevant documents found in the directory to answer the question."

# Test 3: Handling missing query (no key in Redis)
def test_generate_answer_no_query(mock_RAG_generation):
    conv_id = "12345"
    conversation_block_id = "block123"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    mock_RAG_generation.redis_client.get_query = MagicMock(
        return_value=f"No query found in Redis for key: {conversation_block_id}:{conv_id}"
    )

    directory_path = "/fake/path"

    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_RAG_generation.file_reader.read_files.assert_called_once_with(directory_path)
    assert result == "The meaning of life is 42."

# Test 4: Handling invalid directory path (no files to read)
def test_generate_answer_invalid_directory(mock_RAG_generation):
    mock_RAG_generation.file_reader.read_files = MagicMock(return_value="")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/invalid/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    assert result == "No relevant documents found in the directory to answer the question."

# Test 5: Handling missing query and empty directory (both fail)
def test_generate_answer_no_query_no_context(mock_RAG_generation):
    conv_id = "12345"
    conversation_block_id = "block123"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    mock_RAG_generation.redis_client.get_query = MagicMock(
        return_value=f"No query found in Redis for key: {conversation_block_id}:{conv_id}"
    )
    mock_RAG_generation.file_reader.read_files = MagicMock(return_value="")

    directory_path = "/fake/path"

    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    assert result == "No relevant documents found in the directory to answer the question."

# Test 6: Handling case where LLMHandler returns an empty answer
def test_generate_answer_empty_llm_response(mock_RAG_generation):
    mock_RAG_generation.llm_handler.generate_answer = MagicMock(return_value="")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    assert result == ""

# Test 7: Handling query with context containing multiple documents
def test_generate_answer_multiple_context(mock_RAG_generation):
    mock_RAG_generation.file_reader.read_files = MagicMock(return_value="Document 1 content. Document 2 content.")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_RAG_generation.llm_handler.generate_answer.assert_called_once_with(
        question="What is the meaning of life?",
        context="Document 1 content. Document 2 content."
    )
    assert result == "The meaning of life is 42."

# Test 8: Handling empty Redis and context but valid LLM query still processed
def test_generate_answer_no_redis_valid_context(mock_RAG_generation):
    conv_id = "12345"
    conversation_block_id = "block123"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    mock_RAG_generation.redis_client.get_query = MagicMock(
        return_value=f"No query found in Redis for key: {conversation_block_id}:{conv_id}"
    )
    mock_RAG_generation.file_reader.read_files = MagicMock(return_value="Valid context from documents.")

    directory_path = "/fake/path"

    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_RAG_generation.llm_handler.generate_answer.assert_called_once_with(
        question=f"No query found in Redis for key: {conversation_block_id}:{conv_id}",
        context="Valid context from documents."
    )
    assert result == "The meaning of life is 42."

# Test 9: Handling Redis failure (connection error or timeout)
def test_generate_answer_redis_failure(mock_RAG_generation):
    mock_RAG_generation.redis_client.get_query = MagicMock(side_effect=Exception("Redis connection error"))

    conv_id = "12345"
    conversation_block_id = "block123"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    directory_path = "/fake/path"

    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_RAG_generation.llm_handler.generate_answer.assert_called_once_with(
        question="No query found due to Redis error: Redis connection error",
        context="The meaning of life is to give life a meaning."
    )
    assert result == "The meaning of life is 42."

# Test 10: Handling missing query and empty context (no LLM call)
def test_generate_answer_no_query_no_context_no_llm_call(mock_RAG_generation):
    conv_id = "12345"
    conversation_block_id = "block123"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    mock_RAG_generation.redis_client.get_query = MagicMock(
        return_value=f"No query found in Redis for key: {conversation_block_id}:{conv_id}"
    )
    mock_RAG_generation.file_reader.read_files = MagicMock(return_value="")

    directory_path = "/fake/path"

    result = mock_RAG_generation.generate_answer(redis_key, directory_path)

    mock_RAG_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_RAG_generation.file_reader.read_files.assert_called_once_with(directory_path)
    mock_RAG_generation.llm_handler.generate_answer.assert_not_called()
    assert result == "No relevant documents found in the directory to answer the question."

# Test 11: Verify normal operation with valid query in GPT mode
def test_generate_answer_gpt_mode(mock_GPT_generation):
    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question="What is the meaning of life?"
    )
    assert result == "The meaning of life is 42."

# Test 12: Handling empty question in GPT mode
def test_generate_answer_gpt_mode_empty_question(mock_GPT_generation):
    mock_GPT_generation.redis_client.get_query = MagicMock(return_value="")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question=""
    )
    assert result == "The meaning of life is 42."

# Test 13: Handling special characters in question in GPT mode
def test_generate_answer_gpt_mode_special_characters(mock_GPT_generation):
    mock_GPT_generation.redis_client.get_query = MagicMock(return_value="What about special characters like @#$%^&*()?")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question="What about special characters like @#$%^&*()?"
    )
    assert result == "The meaning of life is 42."

# Test 14: Handling numeric question in GPT mode
def test_generate_answer_gpt_mode_numeric_question(mock_GPT_generation):
    mock_GPT_generation.redis_client.get_query = MagicMock(return_value="What is 1234567890?")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question="What is 1234567890?"
    )
    assert result == "The meaning of life is 42."

# Test 15: Handling long question in GPT mode
def test_generate_answer_gpt_mode_long_question(mock_GPT_generation):
    long_question = "What is the meaning of life?" * 100
    mock_GPT_generation.redis_client.get_query = MagicMock(return_value=long_question)

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question=long_question
    )
    assert result == "The meaning of life is 42."

# Test 16: Handling mixed input in GPT mode
def test_generate_answer_gpt_mode_mixed_input(mock_GPT_generation):
    mock_GPT_generation.redis_client.get_query = MagicMock(return_value="Mix of numbers 123, special chars @#&, and letters.")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question="Mix of numbers 123, special chars @#&, and letters."
    )
    assert result == "The meaning of life is 42."

# Test 17: Handling Unicode characters in GPT mode
def test_generate_answer_gpt_mode_unicode_characters(mock_GPT_generation):
    mock_GPT_generation.redis_client.get_query = MagicMock(return_value="What about Unicode characters like 😊, 你好, and مرحبا?")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question="What about Unicode characters like 😊, 你好, and مرحبا?"
    )
    assert result == "The meaning of life is 42."

# Test 18: Handling edge case question in GPT mode
def test_generate_answer_gpt_mode_edge_case_question(mock_GPT_generation):
    mock_GPT_generation.redis_client.get_query = MagicMock(return_value="What is the airspeed velocity of an unladen swallow?")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question="What is the airspeed velocity of an unladen swallow?"
    )
    assert result == "The meaning of life is 42."

# Test 19: Handling HTML content in question in GPT mode
def test_generate_answer_gpt_mode_html_content(mock_GPT_generation):
    mock_GPT_generation.redis_client.get_query = MagicMock(return_value="<p>What is the meaning of <strong>life</strong>?</p>")

    conv_id = "12345"
    conversation_block_id = "block123"
    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question="<p>What is the meaning of <strong>life</strong>?</p>"
    )
    assert result == "The meaning of life is 42."

# Test 20: Handling empty Redis and valid LLM query in GPT mode
def test_generate_answer_gpt_mode_no_redis_valid_query(mock_GPT_generation):
    conv_id = "12345"
    conversation_block_id = "block123"
    mock_GPT_generation.redis_client.get_query = MagicMock(
        return_value=f"No query found in Redis for key: {conversation_block_id}:{conv_id}"
    )

    directory_path = "/fake/path"
    redis_key = f"{str(conversation_block_id)}:{conv_id}"
    result = mock_GPT_generation.generate_answer(redis_key, directory_path)

    mock_GPT_generation.redis_client.get_query.assert_called_once_with(redis_key)
    mock_GPT_generation.llm_handler.generate_answer.assert_called_once_with(
        question=f"No query found in Redis for key: {conversation_block_id}:{conv_id}"
    )
    assert result == "The meaning of life is 42."
