from services.common.config import LOCAL_FOLDER

import os
import json
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def check_stored_docs():
    vectorstore = Chroma(
        collection_name="summaries", 
        embedding_function=OpenAIEmbeddings(),
        persist_directory=LOCAL_FOLDER
    )

    count = vectorstore._collection.count()
    try:
        all_docs = vectorstore.similarity_search("", k=count) 
        if not all_docs:
            print("No documents stored in the vector database.")
        else:
            for doc in all_docs:
                print(f"Document ID: {doc.metadata.get('doc_id')},  Document Type: {doc.metadata.get('doc_type')}")
                # Uncomment the line below to preview the document content
                # print(f"Document Content (Preview): {doc.page_content[:100]}...")
    except Exception as e:
        print(f"Error occurred while retrieving documents: {str(e)}")

def delete_document_by_id(doc_id_to_delete):
    # Loading local Chroma vector database
    vectorstore = Chroma(
        collection_name="summaries", 
        embedding_function=OpenAIEmbeddings(),
        persist_directory=LOCAL_FOLDER
    )
    try:
        count = vectorstore._collection.count()
        all_docs = vectorstore.similarity_search("", k=count) 
        doc_exists = any(doc.metadata.get('doc_id') == doc_id_to_delete for doc in all_docs)
        if not doc_exists:
            print(f"Document with doc_id {doc_id_to_delete} does not exist. Skipping deletion.")
            return
        
        vectorstore._collection.delete(ids=doc_id_to_delete)
        doc_id_file_path = os.path.join(LOCAL_FOLDER, "doc_id.json")
        if os.path.exists(doc_id_file_path):
            with open(doc_id_file_path, 'r', encoding='utf-8') as f:
                doc_ids = json.load(f)

            # Remove deleted doc_id from doc_id.json
            if doc_id_to_delete in doc_ids:
                doc_ids.remove(doc_id_to_delete)
                print(f"Removed doc_id {doc_id_to_delete} from doc_id.json")

            # Update doc_id list
            with open(doc_id_file_path, 'w', encoding='utf-8') as f:
                json.dump(doc_ids, f, indent=4)
    
    except Exception as e:
        print(f"Error occurred while deleting document: {str(e)}")


if __name__ == "__main__":
    while True:
        print("\nPlease choose an option:")
        print("1. Check stored documents")
        print("2. Delete document by ID")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice == '1':
            check_stored_docs()
        elif choice == '2':
            doc_id_to_delete = input("Enter the doc_id of the document you want to delete: ").strip()
            delete_document_by_id(doc_id_to_delete)
        elif choice == '3':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
