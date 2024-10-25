import os  # Standard library imports

import redis  # Third-party imports
from docx import Document as DocxReader  # For reading .docx files

from services.common.config import REDIS_HOST, REDIS_PORT  # Local application imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class Generation:
    """
    A class to generate answers to user queries based on context from text and Word documents.

    This class reads content from .txt and .docx files in a specified directory,
    retrieves user queries from Redis, and uses a language model to generate answers
    based on the provided context and queries.
    """

    def __init__(self):
        """
        Initialize the Generation class by setting up the language model,
        prompt template, and Redis client.
        """
        # Initialize the language model
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

        # Define the prompt template
        self.prompt_template = (
            "Answer the question based only on the following context:\n"
            "{context}\n\n"
            "Question: {question}\n"
        )
        self.prompt = ChatPromptTemplate.from_template(self.prompt_template)

        # Initialize the Redis client
        self.redis_client = redis.StrictRedis(
            host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
        )

    def read_files(self, directory_path: str) -> str:
        """
        Read all .txt and .docx files in the specified directory and return their combined content as context.

        Parameters
        ----------
        directory_path : str
            The path to the directory containing the files.

        Returns
        -------
        str
            A string containing the concatenated content of all .txt and .docx files.
        """
        context = ""

        # Loop through all files in the specified directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            if filename.endswith(".txt"):
                # Open and read the .txt file content
                with open(file_path, 'r', encoding='utf-8') as file:
                    context += file.read() + "\n"  # Add newline between file contents

            elif filename.endswith(".docx"):
                # Read the .docx file content using python-docx
                doc = DocxReader(file_path)
                full_text = [para.text for para in doc.paragraphs]
                context += '\n'.join(full_text) + "\n"  # Add newline between file contents

        return context

    def generate_answer(self, conv_id: str, directory_path: str) -> str:
        """
        Generate an answer based on the query and the context retrieved from the files.

        Parameters
        ----------
        conv_id : str
            The user's conversation ID.
        directory_path : str
            Path to the directory containing the files to read as context.

        Returns
        -------
        str
            The generated answer as a string.
        """
        query = self.query_from_redis(conv_id)
        context = self.read_files(directory_path)

        # Check if we have any context from the files
        if not context:
            return "No relevant documents found in the directory to answer the question."

        # Create a prompt by filling in the context and question in the template
        filled_prompt = self.prompt.format(context=context, question=query)

        # Run the prompt through the language model
        answer = self.llm.invoke(filled_prompt)

        return answer.content  # Return the generated answer

    def query_from_redis(self, conv_id: str) -> str:
        """
        Retrieve the user's query from Redis using the provided conversation ID.

        Parameters
        ----------
        conv_id : str
            The conversation ID used to fetch the query from Redis.

        Returns
        -------
        str
            The query stored in Redis for the provided ID, or an error message if not found.
        """
        redis_key = f"query:{conv_id}"
        try:
            # Fetch the query from Redis by conversation ID
            query = self.redis_client.get(redis_key)

            if query:
                return query
            else:
                return f"No query found in Redis for conversation ID: {conv_id}"

        except Exception as e:
            return f"Error while fetching query from Redis: {str(e)}"


# Example usage:
# if __name__ == "__main__":
#     directory_path = r"E:\HiData\Microservice_RAG\test_output"
#     conv_id = '12345'  # Example conversation ID
#     generation = Generation()
#     # Generate an answer based on the files in the directory
#     answer = generation.generate_answer(conv_id, directory_path)
#     print("Generated Answer:", answer)
