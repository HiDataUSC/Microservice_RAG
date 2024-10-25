from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from services.common.config import LOCAL_FOLDER

class VectorStore:
    def __init__(self, local_folder=LOCAL_FOLDER):
        self.local_folder = local_folder
        self.vectorstore = Chroma(
            collection_name="summaries",
            embedding_function=OpenAIEmbeddings(),
            persist_directory=self.local_folder
        )

    def similarity_search(self, query, k=1):
        return self.vectorstore.similarity_search(query, k=k)
