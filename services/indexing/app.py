from services.common import config # Load common file
from services.indexing.file_processing_states import detect_file_type, FileProcessingState
from services.indexing.AWS_handler import S3Handler
from services.indexing.helper import FileUUIDGenerator, LocalFileByteStore

class Preprocessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.local_folder = r"E:\HiData\Microservice_RAG\services\indexing\local_folder"
        self.state = self.set_state()
        self.doc_id = FileUUIDGenerator(self.local_folder).generate_unique_uuid()
        

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
        self.store_cloud()
    
    def retrieve(self, query):
        return self.state.retrieve(query, self.local_folder)
    
    def store_cloud(self):
        """Upload the original file to cloud database."""
        s3_handler = S3Handler()
        s3_handler.upload_file(self.file_path, object_name=self.doc_id)
        return 0
        
if __name__ == "__main__":
    # need to be absolute path
    file_path = r"E:\HiData\Microservice_RAG\tests\test.txt"
    # Initialize Preprocessor
    preprocessor = Preprocessor(file_path)

    # store file with file_path
    preprocessor.process()

    # search for file
    # query = "Memory in agents"
    # sub_doc = preprocessor.retrieve(query)
    # print(sub_doc)