from services.common.AWS_handler import S3Handler
from services.retrieval.redis_client import RedisClient
from services.retrieval.vector_store import VectorStore

class Retriever:
    """Class to handle document retrieval from local vector store and downloading full documents from S3."""
    def __init__(self):
        """Initialize the Retrieve class with a local folder for persistence of vector store data."""
        self.redis_handler = RedisClient()
        self.vector_store = VectorStore()
        self.s3_handler = S3Handler()

    def store_query_in_redis(self, query, conversation_block_id,**kwargs):
        """
        Store the query in Redis.
        
        :param query: The query string to store in Redis.
        :param conv_id: The conversation ID to store the query under.
        :param sender_id: The sender ID to store the query under.
        """
        return self.redis_handler.store_query(query, conversation_block_id,**kwargs)

    def retrieve(self, query, content_keys = None):
        """
        Perform a similarity search in the vector store using the provided query.
        
        :param query: The query string to search for similar documents in the vector store.
        :param content_keys: The content keys to search for similar documents in the vector store.
        :return: The top similar document(s) based on the query.
        """
        return self.vector_store.similarity_search(query, content_keys, k=1)
    
    def full_document(self, doc_id, dst_folder):
        """
        Download the full document from S3 using the doc_id and save it to the specified destination folder.
        
        :param doc_id: The unique document identifier used to locate the file in S3.
        :param dst_folder: The destination folder where the document will be downloaded.
        """
        self.s3_handler.download_file(folder_prefix = "files", object_name_prefix = doc_id, dst_folder=dst_folder)
