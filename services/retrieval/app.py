from services.common.config import LOCAL_FOLDER # Load common file
from services.common.AWS_handler import S3Handler

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class Retriever:
    """Class to handle document retrieval from local vector store and downloading full documents from S3."""
    def __init__(self, local_folder):
        """Initialize the Retrieve class with a local folder for persistence of vector store data."""
        self.local_folder = local_folder

    def retrieve(self, query):
        """
        Perform a similarity search in the vector store using the provided query.
        
        :param query: The query string to search for similar documents in the vector store.
        :return: The top similar document(s) based on the query.
        """
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

    
if __name__ == "__main__":
    # Initialize Preprocessor
    retriever = Retriever(LOCAL_FOLDER)

    # store file with file_path
    query = "Memory in agents"
    for doc in retriever.retrieve(query):
        doc_id = doc.metadata.get('doc_id')
    dst_folder = r"E:\HiData\Microservice_RAG\tests"
    retriever.full_document(doc_id, dst_folder)