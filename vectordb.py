# Handles vector database operations using FAISS
import faiss
import numpy as np
import uuid
import sqlite3

DB_PATH = 'sessions.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        thread_id TEXT,
        file_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

class VectorDB:
    def __init__(self, dim, db_path=None):
        self.dim = dim
        self.db_path = db_path
        self.index = faiss.IndexFlatL2(dim)
        self.data = []

    def add(self, vectors, metadata):
        self.index.add(np.array(vectors).astype('float32'))
        self.data.extend(metadata)

    def search(self, query_vector, top_k=5):
        D, I = self.index.search(np.array([query_vector]).astype('float32'), top_k)
        return [self.data[i] for i in I[0] if i < len(self.data)]
