from services.generation.redis_client import RedisClient
from services.generation.file_reader import FileReader
from services.generation.llm_handler import LLMHandler

class Generation:
    def __init__(self, mode='RAG'):
        self.mode = mode
        self.redis_client = RedisClient()
        self.file_reader = FileReader()
        self.llm_handler = LLMHandler(mode)

    def generate_answer(self, conv_id: str, directory_path: str) -> str:
        """
        Generate an answer based on the specified mode.
        
        :param conv_id: Conversation ID to retrieve the query from Redis.
        :param directory_path: Directory path to read context files (used in RAG mode).
        :return: Generated answer as a string.
        """
        try:
            query = self.redis_client.get_query(conv_id)
        except Exception as e:
            query = f"No query found due to Redis error: {str(e)}"

        if self.mode == 'RAG':
            context = self.file_reader.read_files(directory_path)
            if not context:
                return "No relevant documents found in the directory to answer the question."
            return self.llm_handler.generate_answer(question=query, context=context)
        
        elif self.mode == 'GPT':
            # In GPT mode, context is not used, only the query is needed.
            return self.llm_handler.generate_answer(question=query)
        
        else:
            return "Unsupported mode. Please use 'RAG' or 'GPT'."

