# api_server.py

import os
import shutil
from flask import Flask, request, jsonify
from services.file_management.serviceManager import RedisManager
from services.indexing.app import Preprocessor
from services.retrieval.app import Retriever
from services.generation.app import Generation

app = Flask(__name__)
redis_manager = RedisManager()
redis_manager.init()

class DocumentService:
    def __init__(self):
        self.dst_folder = r"E:\HiData\Microservice_RAG\test_output"

    def upload_document(self, file_path):
        """Handles document uploading"""
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist.", 400

        try:
            Preprocessor(file_path).process()
            return f"Document uploaded successfully: {file_path}", 200
        except Exception as e:
            return f"Error uploading document: {e}", 500

    def retrieve_document(self, query):
        """Handles document retrieval based on a query."""
        retriever = Retriever()
        generator = Generation()
        try:
            conv_id = retriever.store_query_in_redis(query)
            docs = retriever.retrieve(query)
            doc = next(iter(docs), None)
            if not doc:
                return "No documents found for the query.", 404

            doc_id = doc.metadata.get('doc_id')
            retriever.full_document(doc_id, self.dst_folder)
            answer = generator.generate_answer(conv_id, self.dst_folder)
            return answer, 200
        except Exception as e:
            return f"Error retrieving document: {e}", 500
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleans up the destination folder by removing all files."""
        for filename in os.listdir(self.dst_folder):
            file_path = os.path.join(self.dst_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file or link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the directory
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

# Initialize DocumentService
doc_service = DocumentService()

@app.route('/upload', methods=['POST'])
def upload_document():
    file_path = request.json.get('file_path')
    if not file_path:
        return jsonify({'error': 'File path is required'}), 400

    message, status_code = doc_service.upload_document(file_path)
    return jsonify({'message': message}), status_code

@app.route('/retrieve', methods=['POST'])
def retrieve_document():
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'Query is required'}), 400

    answer, status_code = doc_service.retrieve_document(query)
    if status_code == 200:
        return jsonify({'answer': answer}), 200
    else:
        return jsonify({'error': answer}), status_code

@app.route('/cleanup', methods=['POST'])
def cleanup():
    doc_service.cleanup()
    return jsonify({'message': 'Cleanup complete'}), 200

@app.route('/shutdown', methods=['POST'])
def shutdown():
    redis_manager.stop_redis()
    return jsonify({'message': 'Redis stopped and server shutdown'}), 200

if __name__ == '__main__':
    app.run(port=5000)
