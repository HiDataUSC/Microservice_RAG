from services.generation.redis_client import RedisClient
from services.generation.file_reader import FileReader
from services.generation.llm_handler import LLMHandler

class Generation:
    def __init__(self, mode='RAG'):
        self.mode = mode
        self.redis_client = RedisClient()
        self.file_reader = FileReader()
        self.llm_handler = LLMHandler(mode)

    def generate_answer(self, redis_key: str, directory_path: str) -> str:
        """
        Generate an answer based on the specified mode.
        :param conv_id: Conversation ID to retrieve the query from Redis.
        :param directory_path: Directory path to read context files (used in RAG mode).
        :param conversation_block_id: Block ID for the conversation.
        :return: Generated answer as a string.
        """
        parts = redis_key.split(':')
        conversation_block_id = parts[0]
        conv_id = parts[1]
        try:
            query = self.redis_client.get_query(redis_key)
        except Exception as e:
            query = f"No query found due to Redis error: {str(e)}"

        if self.mode == 'RAG':
            context = self.file_reader.read_files(directory_path)
            if not context:
                answer = "No relevant documents found in the directory to answer the question."
            else:
                answer = self.llm_handler.generate_answer(question=query, context=context)
        elif self.mode == 'GPT':
            answer = self.llm_handler.generate_answer(question=query)
        else:
            answer = "Unsupported mode. Please use 'RAG' or 'GPT'."

        # 存储答案到 Redis
        try:
            self.redis_client.store_query(
                query=answer,
                conversation_block_id=conversation_block_id,
                sender_id='ai'  # 标识这是 AI 的回答
            )
        except Exception as e:
            print(f"Error storing AI response: {str(e)}")

        return answer

