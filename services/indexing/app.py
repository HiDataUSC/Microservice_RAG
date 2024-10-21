from services.common import config # Load common file
from services.indexing.file_processing_states import detect_file_type, FileProcessingState
from services.indexing.AWS_handler import S3Handler

import boto3
from pathlib import Path
import mimetypes

class Preprocessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.state = self.set_state()
        self.vectors = self.process()

    def set_state(self):
        """Set the current processing state (file type)."""
        return detect_file_type(self.file_path)
    
    def process(self):
        """Process the file by reading, preprocessing, and vectorizing."""
        if self.state is None:
            raise ValueError("Processing state (file type) not set.")

        # Step 1: Read the file
        content = self.state.read(self.file_path)

        # Step 2: Preprocess the content
        preprocessed_content = self.state.preprocess(content)

        # Step 3: Vectorize the preprocessed content
        vectors = self.state.vectorize(preprocessed_content)
        print(len(vectors))
        print(vectors)
        return vectors
    
    def upload_original_file(self):
        """Upload the original file to cloud database."""
        return 0
    
    def upload_vectorized_file(self):
        """Upload the processed file to cloud database."""
        s3_handler = S3Handler()
        s3_handler.upload_file('path/to/local/file.txt')
        return 0

        
if __name__ == "__main__":
    # need to be absolute path
    file_path = r"E:\HiData\Microservice_RAG\services\indexing\test.txt"
    # Initialize Preprocessor
    preprocessor = Preprocessor(file_path)
    print(preprocessor.state)