from services.generation.redis_client import RedisClient
from services.generation.file_reader import FileReader
from services.generation.llm_handler import LLMHandler

class Generation:
    def __init__(self):
        self.redis_client = RedisClient()
        self.file_reader = FileReader()
        self.llm_handler = LLMHandler()

    def generate_answer(self, conv_id: str, directory_path: str) -> str:
        try:
            query = self.redis_client.get_query(conv_id)
        except Exception as e:
            query = f"No query found due to Redis error: {str(e)}"

        context = self.file_reader.read_files(directory_path)
        if not context:
            return "No relevant documents found in the directory to answer the question."

        return self.llm_handler.generate_answer(context, query)

