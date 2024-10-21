import os
from abc import ABC, abstractmethod
from pathlib import Path
import mimetypes
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


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
    def vectorize(self, content):
        """Vectorize the preprocessed content."""
        pass


# State for processing text files
class TextFileState(FileProcessingState):
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.embeddings = OpenAIEmbeddings()

    def read(self, file_path):
        """Read the text file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def preprocess(self, content):
        """Preprocess by splitting the text."""
        return self.text_splitter.split_text(content)

    def vectorize(self, content):
        """Vectorize the text chunks."""
        vectorstore = Chroma.from_texts(texts=content, embedding=self.embeddings)
        return vectorstore


# State for processing PDF files (Placeholder, actual implementation needed)
class PDFFileState(FileProcessingState):
    def read(self, file_path):
        """Read and extract text from PDF (simplified)."""
        print(f"Reading PDF file: {file_path}")
        # Use a library like pdfminer to extract text (here it's a placeholder)
        return "Extracted text from PDF"

    def preprocess(self, content):
        """Preprocess by splitting the extracted text."""
        print("Preprocessing PDF content...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return text_splitter.split_text(content)

    def vectorize(self, content):
        """Vectorize the PDF content."""
        print("Generating embeddings for PDF...")
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_texts(texts=content, embedding=embeddings)
        return vectorstore


# State for processing Word files (Placeholder, actual implementation needed)
class WordFileState(FileProcessingState):
    def read(self, file_path):
        """Read and extract text from Word document (simplified)."""
        print(f"Reading Word file: {file_path}")
        # Use a library like python-docx to extract text (here it's a placeholder)
        return "Extracted text from Word document"

    def preprocess(self, content):
        """Preprocess by splitting the extracted text."""
        print("Preprocessing Word content...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return text_splitter.split_text(content)

    def vectorize(self, content):
        """Vectorize the Word content."""
        print("Generating embeddings for Word document...")
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_texts(texts=content, embedding=embeddings)
        return vectorstore


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
