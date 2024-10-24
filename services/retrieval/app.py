from services.common.config import LOCAL_FOLDER, REDIS_HOST, REDIS_PORT # Load common file
from services.common.AWS_handler import S3Handler

import redis
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class Retriever:
    """Class to handle document retrieval from local vector store and downloading full documents from S3."""
    def __init__(self, local_folder = LOCAL_FOLDER):
        """Initialize the Retrieve class with a local folder for persistence of vector store data."""
        self.local_folder = local_folder
        self.redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

    def store_query_in_redis(self, query):
        """
        Store the query in Redis with an auto-incrementing key.
        
        :param query: The query string to store in Redis.
        """
        # Increment a key to act as the query ID
        query_id = self.redis_client.incr('query_id')
        # Store the query with the incremented query_id as the key
        self.redis_client.set(f'query:{query_id}', query)
        return query_id

    def retrieve(self, query):
        """
        Perform a similarity search in the vector store using the provided query.
        
        :param query: The query string to search for similar documents in the vector store.
        :return: The top similar document(s) based on the query.
        """
        try:
            query_id = self.store_query_in_redis(query)
            print(f"Query stored in Redis with ID: {query_id}")
        except Exception:
            pass

        vectorstore = Chroma(
            collection_name="summaries", 
            embedding_function=OpenAIEmbeddings(),
            persist_directory=self.local_folder
        )
        return vectorstore.similarity_search(query, k=1)
    
    def full_document(self, doc_id, dst_folder):
        """
        Download the full document from S3 using the doc_id and save it to the specified destination folder.
        
        :param doc_id: The unique document identifier used to locate the file in S3.
        :param dst_folder: The destination folder where the document will be downloaded.
        """
        # Initialize S3 handler and download the file from S3 using the doc_id
        s3_handler = S3Handler()
        s3_handler.download_file(doc_id, dst_folder)

    
# if __name__ == "__main__":
#     # Initialize Preprocessor
#     retriever = Retriever(LOCAL_FOLDER)

#     # store file with file_path
#     query = "Memory in agents"
#     for doc in retriever.retrieve(query):
#         doc_id = doc.metadata.get('doc_id')
#     dst_folder = r"E:\HiData\Microservice_RAG\tests"
#     retriever.full_document(doc_id, dst_folder)