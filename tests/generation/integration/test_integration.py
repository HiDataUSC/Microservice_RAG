import pytest
from unittest.mock import MagicMock
from services.generation.app import Generation

@pytest.fixture
def mock_generation():
    # Create a Generation instance with mocked dependencies
    generation = Generation()

    # Mock RedisClient behavior
    generation.redis_client.get_query = MagicMock(return_value="What is the meaning of life?")

    # Mock FileReader behavior
    generation.file_reader.read_files = MagicMock(return_value="The meaning of life is to give life a meaning.")

    # Mock LLMHandler behavior
    generation.llm_handler.generate_answer = MagicMock(return_value="The meaning of life is 42.")

    return generation

# Test 1: Verify normal operation with valid query and context
def test_generate_answer(mock_generation):
    conv_id = "12345"
    directory_path = "/fake/path"

    # Call the method
    result = mock_generation.generate_answer(conv_id, directory_path)

    # Assertions
    mock_generation.redis_client.get_query.assert_called_once_with(conv_id)
    mock_generation.file_reader.read_files.assert_called_once_with(directory_path)
    mock_generation.llm_handler.generate_answer.assert_called_once_with(
        "The meaning of life is to give life a meaning.", "What is the meaning of life?"
    )

    assert result == "The meaning of life is 42."

# Test 2: Handling empty context (empty directory)
def test_generate_answer_no_context(mock_generation):
    # Simulate an empty directory
    mock_generation.file_reader.read_files = MagicMock(return_value="")

    conv_id = "12345"
    directory_path = "/fake/path"

    result = mock_generation.generate_answer(conv_id, directory_path)

    # Check the correct message is returned when no context is found
    assert result == "No relevant documents found in the directory to answer the question."

# Test 3: Handling missing query (no key in Redis)
def test_generate_answer_no_query(mock_generation):
    # Simulate no query found in Redis
    mock_generation.redis_client.get_query = MagicMock(return_value="No query found in Redis for conversation ID: 12345")

    conv_id = "12345"
    directory_path = "/fake/path"

    result = mock_generation.generate_answer(conv_id, directory_path)

    # Ensure the function still tries to proceed with the available context
    mock_generation.file_reader.read_files.assert_called_once_with(directory_path)

    # Since there's context, it should still generate an answer
    assert result == "The meaning of life is 42."

# Test 4: Handling invalid directory path (no files to read)
def test_generate_answer_invalid_directory(mock_generation):
    # Simulate invalid directory path (FileReader returns empty context)
    mock_generation.file_reader.read_files = MagicMock(return_value="")

    conv_id = "12345"
    directory_path = "/invalid/path"

    result = mock_generation.generate_answer(conv_id, directory_path)

    # Expect the method to handle invalid directory gracefully
    assert result == "No relevant documents found in the directory to answer the question."

# Test 5: Handling missing query and empty directory (both fail)
def test_generate_answer_no_query_no_context(mock_generation):
    # Simulate no query in Redis and no relevant documents
    mock_generation.redis_client.get_query = MagicMock(return_value="No query found in Redis for conversation ID: 12345")
    mock_generation.file_reader.read_files = MagicMock(return_value="")

    conv_id = "12345"
    directory_path = "/fake/path"

    result = mock_generation.generate_answer(conv_id, directory_path)

    # Check the correct message is returned when both fail
    assert result == "No relevant documents found in the directory to answer the question."

# Test 6: Handling case where LLMHandler returns an empty answer
def test_generate_answer_empty_llm_response(mock_generation):
    # Simulate the LLM returning an empty response
    mock_generation.llm_handler.generate_answer = MagicMock(return_value="")

    conv_id = "12345"
    directory_path = "/fake/path"

    result = mock_generation.generate_answer(conv_id, directory_path)

    # Ensure the function handles empty LLM response properly
    assert result == ""

# Test 7: Handling query with context containing multiple documents
def test_generate_answer_multiple_context(mock_generation):
    # Simulate reading multiple documents from directory
    mock_generation.file_reader.read_files = MagicMock(return_value="Document 1 content. Document 2 content.")

    conv_id = "12345"
    directory_path = "/fake/path"

    result = mock_generation.generate_answer(conv_id, directory_path)

    # Ensure the LLM generates an answer based on combined context
    mock_generation.llm_handler.generate_answer.assert_called_once_with(
        "Document 1 content. Document 2 content.", "What is the meaning of life?"
    )
    assert result == "The meaning of life is 42."

# Test 8: Handling empty Redis and context but valid LLM query still processed
def test_generate_answer_no_redis_valid_context(mock_generation):
    # Simulate no query found in Redis but valid context
    mock_generation.redis_client.get_query = MagicMock(return_value="No query found in Redis for conversation ID: 12345")
    mock_generation.file_reader.read_files = MagicMock(return_value="Valid context from documents.")

    conv_id = "12345"
    directory_path = "/fake/path"

    result = mock_generation.generate_answer(conv_id, directory_path)

    # Ensure LLM can proceed with valid context even with no Redis query
    mock_generation.llm_handler.generate_answer.assert_called_once_with(
        "Valid context from documents.", "No query found in Redis for conversation ID: 12345"
    )
    assert result == "The meaning of life is 42."

# Test 9: Handling Redis failure (connection error or timeout)
def test_generate_answer_redis_failure(mock_generation):
    # Simulate Redis connection error
    mock_generation.redis_client.get_query = MagicMock(side_effect=Exception("Redis connection error"))

    conv_id = "12345"
    directory_path = "/fake/path"

    result = mock_generation.generate_answer(conv_id, directory_path)

    # Ensure the function handles the Redis failure and generates an appropriate message
    mock_generation.file_reader.read_files.assert_called_once_with(directory_path)
    mock_generation.llm_handler.generate_answer.assert_called_once_with(
        "The meaning of life is to give life a meaning.", "No query found due to Redis error: Redis connection error"
    )
    
    assert result == "The meaning of life is 42."

# Test 10: Handling missing query and empty context (no LLM call)
def test_generate_answer_no_query_no_context_no_llm_call(mock_generation):
    # Simulate no query found in Redis
    mock_generation.redis_client.get_query = MagicMock(return_value="No query found in Redis for conversation ID: 12345")
    # Simulate empty context (no relevant documents)
    mock_generation.file_reader.read_files = MagicMock(return_value="")

    conv_id = "12345"
    directory_path = "/fake/path"

    result = mock_generation.generate_answer(conv_id, directory_path)

    # Ensure that FileReader was called once to attempt reading files
    mock_generation.file_reader.read_files.assert_called_once_with(directory_path)
    
    # Ensure that LLMHandler.generate_answer is never called since there's no query and no context
    mock_generation.llm_handler.generate_answer.assert_not_called()

    # The result should return the appropriate message for no documents and no query
    assert result == "No relevant documents found in the directory to answer the question."


