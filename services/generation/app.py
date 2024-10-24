from services.common.config import REDIS_HOST, REDIS_PORT

import os
import redis
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class Generation:
    def __init__(self):
        """
        Initialize the Generation class with a conversation ID.
        
        :param conv_id: An optional conversation ID to track context across requests.
        """
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)  # Initialize LLM
        self.prompt_template = """Answer the question based only on the following context:
                            {context}

                            Question: {question}
                            """
        self.prompt = ChatPromptTemplate.from_template(self.prompt_template)
        self.redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

    def read_txt_files(self, directory_path):
        """
        Read all .txt files in the specified directory and return their combined content as context.
        
        :param directory_path: The path to the directory containing the .txt files.
        :return: A string containing the concatenated content of all .txt files.
        """
        context = ""
        # Loop through all files in the specified directory
        for filename in os.listdir(directory_path):
            if filename.endswith(".txt"):  # Only process .txt files
                file_path = os.path.join(directory_path, filename)
                # Open and read the file content
                with open(file_path, 'r', encoding='utf-8') as file:
                    context += file.read() + "\n"  # Add newline between file contents
        return context

    def generate_answer(self, conv_id, directory_path):
        """
        Generate an answer based on the query and the context retrieved from the retriever.
        
        :param conv_id: The user's question id.
        :param directory_path: Path to the directory containing the .txt files to read as context.
        :return: The generated answer as a string.
        """
        query = self.query_from_redis(conv_id)
        context = self.read_txt_files(directory_path)
        
        # Check if we have any context from the files
        if not context:
            return "No relevant documents found in the directory to answer the question."
        
        # Create a prompt by filling in the context and question in the template
        filled_prompt = self.prompt.format(context=context, question=query)
        
        # Run the prompt through the LLM using the updated `invoke` method
        answer = self.llm.invoke(filled_prompt)
        
        return answer
    
    def query_from_redis(self, conv_id):
        """
        Retrieve content from Redis using the provided ID.
        
        :param content_id: The ID used to fetch the content from Redis.
        :return: The content stored in Redis for the provided ID, or an error message if not found.
        """
        redis_key = f"query:{conv_id}"
        try:
            # Fetch content from Redis by ID
            content = self.redis_client.get(redis_key)
            
            if content:
                return content
            else:
                return f"No content found in Redis for ID: {redis_key}"
        
        except Exception as e:
            return f"Error while fetching content from Redis: {str(e)}"

# if __name__ == "__main__":
#     directory_path = r"E:\HiData\Microservice_RAG\test_output"
#     generation = Generation()
#     # Generate an answer based on the .txt files in the directory
#     answer = generation.generate_answer(-1, directory_path).content
#     print("Generated Answer:", answer)
