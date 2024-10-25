import sys
import os
import shutil

from services.file_management.serviceManager import RedisManager
from services.indexing.app import Preprocessor
from services.retrieval.app import Retriever
from services.generation.app import Generation


class Main:
    def __init__(self):
        self.dst_folder = r"E:\HiData\Microservice_RAG\test_output"

    def upload_document(self):
        """Handle document uploading via user input."""
        file_path = input("Enter the full path of the document to upload: ").strip()
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return

        print(f"Uploading document from: {file_path}")
        try:
            Preprocessor(file_path).process()
            print(f"Document uploaded successfully: {file_path}")
        except Exception as e:
            print(f"Error uploading document: {e}")

    def retrieve_document(self):
        """Handle document retrieval based on user's query."""
        query = input("Enter your query to retrieve the relevant document: ").strip()
        if not query:
            print("Query cannot be empty.")
            return

        retriever = Retriever()
        generator = Generation()
        try:
            conv_id = retriever.store_query_in_redis(query)
            docs = retriever.retrieve(query)
            doc = next(iter(docs), None)
            if not doc:
                print("No documents found for the query.")
                return

            doc_id = doc.metadata.get('doc_id')
            retriever.full_document(doc_id, self.dst_folder)
            answer = generator.generate_answer(conv_id, self.dst_folder).content
            print(f"\n{answer}")
        except Exception as e:
            print(f"Error retrieving document: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Delete all files in the destination folder."""
        shutil.rmtree(self.dst_folder, ignore_errors=True)


def main():
    """Main program loop to handle user interactions."""
    redis_manager = RedisManager()
    redis_manager.init()
    doc_manager = Main()
    actions = {
        '1': doc_manager.upload_document,
        '2': doc_manager.retrieve_document,
        '3': lambda: sys.exit(0)
    }

    try:
        while True:
            choice = input(
                "\nPlease choose an action:\n"
                "1: Upload a document\n"
                "2: Retrieve a document based on a query\n"
                "3: Exit\n"
                "Enter your choice (1, 2, or 3): "
            ).strip()

            action = actions.get(choice)
            if action:
                if choice == '3':
                    print("Exiting the program. Goodbye!")
                    redis_manager.stop_redis()
                    sys.exit(0)
                action()
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    except KeyboardInterrupt:
        print("\nProgram interrupted with Ctrl+C. Stopping Redis.")
        redis_manager.stop_redis()
        sys.exit(0)
    except SystemExit:
        # Ensure Redis is stopped on sys.exit()
        redis_manager.stop_redis()
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        redis_manager.stop_redis()
        sys.exit(1)


if __name__ == "__main__":
    main()
