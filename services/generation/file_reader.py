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
                    content = file.read()
                    if content.strip():  # Check if content is not empty
                        context += content + "\n"
            elif filename.endswith(".docx"):
                doc = DocxReader(file_path)
                paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
                if paragraphs:  # Check if there are non-empty paragraphs
                    context += '\n'.join(paragraphs) + "\n"
        return context.strip()  # Remove any trailing newlines or spaces
