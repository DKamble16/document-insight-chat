# Handles RAG logic and Gemini API calls
import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_CHAT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"

class RAG:
    def __init__(self, api_key=GEMINI_API_KEY):
        if not api_key or not isinstance(api_key, str) or len(api_key) < 30:
            raise ValueError("A valid Gemini API key must be provided.")
        self.api_key = api_key

    def extract_text_from_xlsx(self, file):
        # Only allow .xlsx files and limit file size for security
        if not hasattr(file, 'name') or not file.name.endswith('.xlsx'):
            raise ValueError("Only .xlsx files are allowed.")
        if hasattr(file, 'size') and file.size > 2 * 1024 * 1024:  # 2MB limit
            raise ValueError("File size exceeds 2MB limit.")
        df = pd.read_excel(file)
        return df.to_string()

    def extract_text_from_file(self, file):
        # Only allow supported file types and limit file size for security
        allowed_exts = ['.xlsx', '.xls', '.csv', '.pdf', '.doc', '.docx']
        if not hasattr(file, 'name') or not any(file.name.lower().endswith(ext) for ext in allowed_exts):
            raise ValueError("Only PDF, DOC/DOCX, XLS/XLSX, and CSV files are allowed.")
        if hasattr(file, 'size') and file.size > 2 * 1024 * 1024:  # 2MB limit for all files
            raise ValueError("File size exceeds 2MB limit.")
        ext = file.name.lower().split('.')[-1]
        if ext in ['xlsx', 'xls']:
            df = pd.read_excel(file)
            return df.to_string()
        elif ext == 'csv':
            df = pd.read_csv(file)
            return df.to_string()
        elif ext in ['pdf', 'doc', 'docx']:
            try:
                import io
                text = ""
                if ext == 'pdf':
                    from PyPDF2 import PdfReader
                    reader = PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() or ""
                else:
                    import docx
                    if ext == 'docx':
                        doc = docx.Document(file)
                        for para in doc.paragraphs:
                            text += para.text + "\n"
                    else:
                        # For .doc, try using textract if available
                        try:
                            import textract
                            text = textract.process(file).decode('utf-8')
                        except Exception:
                            raise ValueError(".doc extraction requires textract and may not work on all systems.")
                return text
            except Exception as e:
                raise ValueError(f"Failed to extract text: {e}")
        else:
            raise ValueError("Unsupported file type.")

    def summarize(self, text):
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        data = {
            "contents": [{"parts": [{"text": f"Summarize this: {text}"}]}]
        }
        response = requests.post(GEMINI_CHAT_URL, headers=headers, params=params, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        elif response.status_code == 403:
            return "API key is invalid or does not have permission."
        else:
            return f"Error: {response.text}"

    def embed(self, text):
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        data = {"content": {"parts": [{"text": text}]}}
        response = requests.post(GEMINI_EMBED_URL, headers=headers, params=params, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()['embedding']['values']
        elif response.status_code == 403:
            return []  # Do not leak error details
        else:
            return []
