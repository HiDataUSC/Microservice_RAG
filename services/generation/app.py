from services.generation.redis_client import RedisClient
from services.generation.file_reader import FileReader
from services.generation.llm_handler import LLMHandler
from typing import List, Dict

class Generation:
    def __init__(self, mode='RAG'):
        self.mode = mode
        self.redis_client = RedisClient()
        self.file_reader = FileReader()
        self.llm_handler = LLMHandler(mode)

    def generate_answer(self, redis_key: str, directory_path: str) -> str:
        """
        Generate an answer based on the specified mode.
        :param redis_key: Combined key containing conversation_block_id and conv_id
        :param directory_path: Directory path to read context files (used in RAG mode)
        :return: Generated answer as a string
        """
        parts = redis_key.split(':')
        conversation_block_id = parts[0]
        conv_id = parts[1]
        try:
            query = self.redis_client.get_query(redis_key)
        except Exception as e:
            query = f"No query found due to Redis error: {str(e)}"

        try:
            chat_history = self.redis_client.get_conversation_history(conversation_block_id)
            formatted_history = self.format_chat_history(chat_history)
        except Exception as e:
            print(f"Error getting chat history: {str(e)}")
            formatted_history = "Error retrieving conversation history."

        if self.mode == 'RAG':
            context = self.file_reader.read_files(directory_path)
            if not context:
                answer = "No relevant documents found in the directory to answer the question."
            else:
                answer = self.llm_handler.generate_answer(
                    question=query,
                    context=context,
                    chat_history=formatted_history
                )
        elif self.mode == 'GPT':
            answer = self.llm_handler.generate_answer(
                question=query,
                chat_history=formatted_history
            )
        else:
            answer = "Unsupported mode. Please use 'RAG' or 'GPT'."

        try:
            self.redis_client.store_query(
                query=answer,
                conversation_block_id=conversation_block_id,
                sender_id='AI'  # 标识这是 AI 的回答
            )
        except Exception as e:
            print(f"Error storing AI response: {str(e)}")

        return answer

    def format_chat_history(self, messages: List[Dict]) -> str:
        formatted_history = []
        for msg in messages:
            role = "Assistant" if msg['sender'] == 'AI' else "User"
            formatted_history.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted_history) if formatted_history else "No previous conversation."
