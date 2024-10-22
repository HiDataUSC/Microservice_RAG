import os
import json
import uuid
from uuid import uuid4

from abc import ABC, abstractmethod
from pathlib import Path
import mimetypes
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.storage import InMemoryByteStore
from langchain.retrievers.multi_vector import MultiVectorRetriever


# Abstract Base State Class for file processing
class FileProcessingState(ABC):
    @abstractmethod
    def read(self, file_path):
        """Read the file."""
        pass
    
    @abstractmethod
    def preprocess(self, content):
        """Preprocess the content."""
        pass

    @abstractmethod
    def vectorize(self, content, local_folder):
        """Vectorize the preprocessed content."""
        pass
    
    @abstractmethod
    def store_local(self, vectorstore, local_folder):
        """Store the vectorized data locally."""
        pass
    
    @abstractmethod
    def retrieve(self, query, local_folder):
        """Retrieve using similarity search."""
        pass


# State for processing text files
class TextFileState(FileProcessingState):
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        self.local_folder = None

    def read(self, file_path):
        """Read the text file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def preprocess(self, content):
        doc = Document(page_content=content)
        chain = (
            {"doc": lambda x: x.page_content}
            | ChatPromptTemplate.from_template("Summarize the following document:\n\n{doc}")
            | ChatOpenAI(model="gpt-3.5-turbo", max_retries=0)
            | StrOutputParser()
        )
        summary = chain.invoke(doc)
        """Preprocess by splitting the text."""
        return summary

    def vectorize(self, local_folder):
        """Vectorize the text chunks."""
        self.local_folder = local_folder
        self.vectorstore = Chroma(
            collection_name="summaries", 
            embedding_function=self.embeddings,
            persist_directory=self.local_folder
        )
        return self.vectorstore
    
    def store_local(self, doc_id, content):
        """Store the document vectors locally."""
        summary_docs = [
            Document(page_content=content, metadata={"doc_id": doc_id})
        ]
        
        # Add the documents to the vectorstore with metadata containing doc_id
        try:
            self.vectorstore.add_documents(summary_docs, ids = [doc_id])
            doc_id_file_path = os.path.join(self.local_folder, "doc_id.json")
            if not os.path.exists(doc_id_file_path):
                # If the file doesn't exist, create it and initialize it with an empty list
                with open(doc_id_file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            with open(doc_id_file_path, 'r', encoding='utf-8') as f:
                doc_ids = json.load(f)
            if doc_id not in doc_ids:
                doc_ids.append(doc_id)
            with open(doc_id_file_path, 'w', encoding='utf-8') as f:
                json.dump(doc_ids, f, indent=4)
        except Exception as e:
            print(f"Error occurred in file_processing_stats.store_local: {str(e)}")

    def retrieve(self, query, local_folder):
        """Retrieve the most similar document."""
        vectorstore = Chroma(
            collection_name="summaries", 
            embedding_function=OpenAIEmbeddings(),
            persist_directory=local_folder
        )
        return vectorstore.similarity_search(query, k=1)
    


# State for processing PDF files (Placeholder, actual implementation needed)
class PDFFileState(FileProcessingState):
    def read(self, file_path):
        """Read the file."""
        pass
    
    def preprocess(self, content):
        """Preprocess the content."""
        pass

    def vectorize(self, content, local_folder):
        """Vectorize the preprocessed content."""
        pass
    
    def store_local(self, vectorstore, local_folder):
        """Store the vectorized data locally."""
        pass
    
    def retrieve(self, query, local_folder):
        """Retrieve using similarity search."""
        pass


# State for processing Word files (Placeholder, actual implementation needed)
class WordFileState(FileProcessingState):
    def read(self, file_path):
        """Read the file."""
        pass
    
    def preprocess(self, content):
        """Preprocess the content."""
        pass

    def vectorize(self, content, local_folder):
        """Vectorize the preprocessed content."""
        pass
    
    def store_local(self, vectorstore, local_folder):
        """Store the vectorized data locally."""
        pass
    
    def retrieve(self, query, local_folder):
        """Retrieve using similarity search."""
        pass


# Utility function to detect file type and return the appropriate state class
def detect_file_type(file_path):
    """Detects file type based on extension."""
    ext = Path(file_path).suffix.lower()
    mime_type, _ = mimetypes.guess_type(file_path)

    if ext == '.txt' or mime_type == 'text/plain':
        return TextFileState()
    elif ext == '.pdf' or mime_type == 'application/pdf':
        return PDFFileState()
    elif ext == '.docx' or mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return WordFileState()
    else:
        return None
