# api_server.py

import os
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from services.file_management.serviceManager import RedisManager
from services.indexing.app import Preprocessor
from services.retrieval.app import Retriever
from services.generation.app import Generation
from services.common.AWS_handler import S3Handler

from services.common.config import LOCAL_FOLDER
from services.common.vectorstore_action import delete_document_by_id

app = Flask(__name__)
CORS(app)
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
                print("No documents found for the query.")
                return

            doc_id = doc.metadata.get('doc_id')
            retriever.full_document(doc_id, self.dst_folder)
            answer = generator.generate_answer(conv_id, self.dst_folder)
            return answer, 200
        except Exception as e:
            return f"Error retrieving document: {e}", 500
        finally:
            self.cleanup()

    def cleanup(self):
        """Delete all files and folders inside the destination folder without deleting the folder itself."""
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
    s3_handler = S3Handler()
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    try:
        file_path = os.path.join(LOCAL_FOLDER, file.filename)
        file.save(file_path)
        message, status_code = doc_service.upload_document(file_path)
        files = s3_handler.read_list(folder_prefix="files")
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({'message': message, 'files': files}), status_code
    except Exception as e:
        print(f"Error during file upload: {e}")
        return jsonify({'error': f"Internal server error: {str(e)}"}), 500

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


@app.route('/download_vectorized_db', methods=['POST'])
def download_vectorized_db():
    """Download all documents from the S3 'files' folder to the local web server."""
    s3_handler = S3Handler()

    try:
        success = s3_handler.download_file(folder_prefix="vectorized_db", dst_folder=LOCAL_FOLDER )
        if success:
            return jsonify({'message': 'All files downloaded successfully.'}), 200
        else:
            return jsonify({'error': 'No files found or download failed.'}), 404
    except Exception as e:
        print(f"Error downloading files: {e}")
        return jsonify({'error': f"Error downloading files: {str(e)}"}), 500

@app.route('/read_file_list', methods=['GET'])
def read_file_list():
    """Read list of files from the S3 'files' folder."""
    s3_handler = S3Handler()

    try:
        files = s3_handler.read_list(folder_prefix="files")
        if files is not None:
            return jsonify({'files': files}), 200
        else:
            return jsonify({'error': 'No files found or error occurred.'}), 404
    except Exception as e:
        print(f"Error listing files: {e}")
        return jsonify({'error': f"Error listing files: {str(e)}"}), 500
    
@app.route('/delete_file', methods=['POST'])
def delete_file():
    """Delete a file from the S3 'files' folder."""
    s3_handler = S3Handler()
    file_key = request.json.get('key')

    if not file_key:
        return jsonify({'error': 'File key is required'}), 400

    try:
        doc_id_to_delete = os.path.splitext(os.path.basename(file_key))[0]
        vectorestore_delete_success = delete_document_by_id(doc_id_to_delete)
        cloud_delete_success = s3_handler.delete_file(file_key)
        if cloud_delete_success and vectorestore_delete_success:
            useful_files = ["chroma.sqlite3", "doc_id.json"]
            for root, _, files in os.walk(LOCAL_FOLDER):
                for file in files:
                    if file in useful_files:
                        file_path = os.path.join(root, file)
                        s3_handler.upload_file(file_path, folder_prefix="vectorized_db", object_name=file)
            return jsonify({'message': 'File deleted successfully.'}), 200
        else:
            return jsonify({'error': 'Failed to delete file.'}), 500
    except Exception as e:
        print(f"Error deleting file: {e}")
        return jsonify({'error': f"Error deleting file: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
