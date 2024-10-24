from services.common.config import LOCAL_FOLDER
from services.indexing.file_processing_states import detect_file_type
from services.common.helper import FileUUIDGenerator

class Preprocessor:
    def __init__(self, file_path, local_folder):
        self.file_path = file_path
        self.local_folder = local_folder
        self.state = self.set_state()
        self.doc_id = FileUUIDGenerator().generate_unique_uuid()
        

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
        self.state.vectorize(self.local_folder)

        # Step 4: Store the vectorized content locally
        self.state.store_local(self.doc_id, preprocessed_content)

        # Step 5: Upload original file with unique ID to cloud storage
        self.state.store_cloud()
        
if __name__ == "__main__":
    # need to be absolute path
    file_path = r"E:\HiData\Microservice_RAG\tests\test.txt"
    # Initialize Preprocessor
    preprocessor = Preprocessor(file_path, LOCAL_FOLDER)
    preprocessor.process()