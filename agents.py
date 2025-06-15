# Defines agents for extraction, summarization, and chat
from rag import RAG
from vectordb import VectorDB
import re
import matplotlib.pyplot as plt
import io
import base64

class ExtractionAgent:
    def __init__(self):
        self.rag = RAG()
    def extract(self, file):
        return self.rag.extract_text_from_xlsx(file)

class SummarizationAgent:
    def __init__(self):
        self.rag = RAG()
    def summarize(self, text):
        return self.rag.summarize(text)

class ChatAgent:
    def __init__(self, vectordb, rag, chunk_size=500, top_k=3):
        self.vectordb = vectordb
        self.rag = rag
        self.chunk_size = chunk_size
        self.top_k = top_k

    def chat(self, query, context_data=None):
        query_vec = self.rag.embed(query)
        docs = self.vectordb.search(query_vec, top_k=self.top_k)
        context = "\n".join(docs)
        prompt = f"You are an expert assistant. Use the following context to answer the user's question as accurately as possible. If the user asks for a chart or graph, generate a Python code block using matplotlib or plotly that can be executed in a Streamlit environment. Only output the code block and nothing else if a chart is requested.\nContext:\n{context}\nQuestion: {query}"
        return self.rag.summarize(prompt)

    @staticmethod
    def extract_code_block(answer):
        # Extract python code block from markdown
        match = re.search(r'```python(.*?)```', answer, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
