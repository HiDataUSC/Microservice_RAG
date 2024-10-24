import sys
import os

from services.indexing.app import Preprocessor
from services.retrieval.app import Retriever


def print_menu():
    """Print the available options for the user."""
    print("\nPlease choose an action:")
    print("1: Upload a document")
    print("2: Retrieve a document based on a query")
    print("3: Exit")


def upload_document_action():
    """Handle document uploading via user input."""
    file_path = input("Please provide the full path of the document you want to upload: ").strip()
    if os.path.exists(file_path):
        print(f"Uploading document from: {file_path}")
        try:
            Preprocessor(file_path).process()
            print(f"Document uploaded successfully: {file_path}")
        except Exception as e:
            print(f"Error uploading document: {e}")
    else:
        print(f"Error: File '{file_path}' does not exist.")


def retrieve_document_action():
    """Handle document retrieval based on user's query."""
    query = input("Please enter your query to retrieve the relevant document: ").strip()
    retriever = Retriever()
    if query:
        print(f"Retrieving document(s) based on query: {query}")
        try:
            for doc in retriever.retrieve(query):
                doc_id = doc.metadata.get('doc_id')
            dst_folder = r"E:\HiData\Microservice_RAG\test_output"
            retriever.full_document(doc_id, dst_folder)
            print(f"file save to: {dst_folder}")
        except Exception as e:
            print(f"Error retrieving document: {e}")
    else:
        print("Query cannot be empty.")


def main():
    """Main program loop to handle user interactions."""
    while True:
        print_menu()
        choice = input("Enter your choice (1, 2, or 3): ").strip()

        if choice == '1':
            upload_document_action()
        elif choice == '2':
            retrieve_document_action()
        elif choice == '3':
            print("Exiting the program. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
