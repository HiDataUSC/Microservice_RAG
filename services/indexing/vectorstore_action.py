import os
import json
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

def check_stored_docs(local_output):
    vectorstore = Chroma(
        collection_name="summaries", 
        embedding_function=OpenAIEmbeddings(),
        persist_directory=local_output
    )

    count = vectorstore._collection.count()
    try:
        all_docs = vectorstore.similarity_search("", k=count) 
        if not all_docs:
            print("No documents stored in the vector database.")
        else:
            for doc in all_docs:
                print(f"Document ID: {doc.metadata.get('doc_id')}")
                # print(f"Document Content (Preview): {doc.page_content[:100]}...")
    except Exception as e:
        print(f"Error occurred while retrieving documents: {str(e)}")

def delete_document_by_id(local_output, doc_id_to_delete):
    # Loading local Chroma vector database
    vectorstore = Chroma(
        collection_name="summaries", 
        embedding_function=OpenAIEmbeddings(),
        persist_directory=local_output
    )
    try:
        count = vectorstore._collection.count()
        all_docs = vectorstore.similarity_search("", k=count) 
        doc_exists = any(doc.metadata.get('doc_id') == doc_id_to_delete for doc in all_docs)
        if not doc_exists:
            print(f"Document with doc_id {doc_id_to_delete} does not exist. Skipping deletion.")
            return
        
        vectorstore._collection.delete(ids=doc_id_to_delete)
        doc_id_file_path = os.path.join(local_output, "doc_id.json")
        if os.path.exists(doc_id_file_path):
            with open(doc_id_file_path, 'r', encoding='utf-8') as f:
                doc_ids = json.load(f)

            # remove deleted doc_id_to_delete from doc_id.json
            if doc_id_to_delete in doc_ids:
                doc_ids.remove(doc_id_to_delete)
                print(f"Removed doc_id {doc_id_to_delete} from doc_id.json")

            # Keep updated doc_id list
            with open(doc_id_file_path, 'w', encoding='utf-8') as f:
                json.dump(doc_ids, f, indent=4)
    
    except Exception as e:
        print(f"Error occurred while deleting document: {str(e)}")


if __name__ == "__main__":
    local_output = r"E:\HiData\Microservice_RAG\services\indexing\local_folder"
    doc_id_to_delete = "cd9e2b68-3fb2-4db3-82a0-59deb936d318"
    delete_document_by_id(local_output, doc_id_to_delete)


# if __name__ == "__main__":
#     local_output = r"E:\HiData\Microservice_RAG\services\indexing\local_folder"
#     check_stored_docs(local_output)
