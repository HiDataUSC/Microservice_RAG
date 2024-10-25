import os
from docx import Document as DocxReader

class FileReader:
    @staticmethod
    def read_files(directory_path: str) -> str:
        context = ""
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if filename.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as file:
                    context += file.read() + "\n"
            elif filename.endswith(".docx"):
                doc = DocxReader(file_path)
                context += '\n'.join([para.text for para in doc.paragraphs]) + "\n"
        return context
