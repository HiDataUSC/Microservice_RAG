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

    def similarity_search(self, query, content_keys=None, k=1):
        if content_keys:
            filter_dict = {"doc_id": {"$in": content_keys}}
            return self.vectorstore.similarity_search(
                query,
                k=k,
                filter=filter_dict
            )
        else:
            # 如果没有指定content_keys，则搜索所有文档
            return self.vectorstore.similarity_search(query, k=k)
