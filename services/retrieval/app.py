from services.common.AWS_handler import S3Handler
from services.retrieval.redis_client import RedisHandler
from services.retrieval.vector_store import VectorStore

class Retriever:
    """Class to handle document retrieval from local vector store and downloading full documents from S3."""
    def __init__(self):
        """Initialize the Retrieve class with a local folder for persistence of vector store data."""
        self.redis_handler = RedisHandler()
        self.vector_store = VectorStore()
        self.s3_handler = S3Handler()

    def store_query_in_redis(self, query):
        """
        Store the query in Redis.
        
        :param query: The query string to store in Redis.
        """
        return self.redis_handler.store_query(query)

    def retrieve(self, query):
        """
        Perform a similarity search in the vector store using the provided query.
        
        :param query: The query string to search for similar documents in the vector store.
        :return: The top similar document(s) based on the query.
        """
        return self.vector_store.similarity_search(query, k=1)
    
    def full_document(self, doc_id, dst_folder):
        """
        Download the full document from S3 using the doc_id and save it to the specified destination folder.
        
        :param doc_id: The unique document identifier used to locate the file in S3.
        :param dst_folder: The destination folder where the document will be downloaded.
        """
        self.s3_handler.download_file(folder_prefix = "files", object_name_prefix = doc_id, dst_folder=dst_folder)
