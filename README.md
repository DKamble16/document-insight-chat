# RAG Gemini Dashboard

A secure, multi-user Streamlit dashboard for Retrieval-Augmented Generation (RAG) using the Gemini API, with business insights, file management, and advanced analytics.

## Features

- **Multi-user session and thread management** (SQLite)
- **Secure file upload** (PDF, DOC/DOCX, XLS/XLSX, CSV; 2MB limit, type/size checks)
- **Persistent file storage** (`uploads/` directory)
- **RAG pipeline**: text extraction, chunking, embedding, FAISS vector DB, Gemini API chat
- **Business insights**: automatic analysis (top products, categories, trends, regions, segments, anomalies, summary stats) with charts
- **Download business insights as PDF** (with charts/images)
- **RAG management UI**: edit, tag, categorize, delete, download, preview files (all in sidebar)
- **Session/thread tracking** in SQLite (`sessions.db`)
- **Modular, security-conscious code** (error handling, user feedback)

## Project Structure

```
project_day4/
├── agents.py                # Extraction, summarization, chat agents
├── business_analyzer.py     # BusinessAnalyzer: insights, charts
├── main.py                  # Streamlit UI, file upload, RAG, insights, PDF
├── rag.py                   # RAG logic, Gemini API, file extraction
├── vectordb.py              # FAISS vector DB, session/thread DB
├── requirements.txt         # All dependencies
├── sessions.db              # SQLite DB for sessions and RAGs
├── uploads/                 # Uploaded files (persistent)
└── myenv/                   # Python virtual environment
```

## Setup & Installation

1. **Clone the repository**
2. **Create and activate a virtual environment**
   ```sh
   python3 -m venv myenv
   source myenv/bin/activate
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the app**
   ```sh
   streamlit run main.py
   ```

## Usage

- Upload a supported file (PDF, DOC/DOCX, XLS/XLSX, CSV)
- View automatic business insights and charts
- Download insights as a PDF (with charts)
- Manage RAGs in the sidebar (edit, tag, categorize, delete, download, preview)
- Chat with your document using Gemini API (RAG)

## Security
- File type and size checks on upload
- All files stored in `uploads/` (not public)
- Session and thread IDs are unique per user
- Error handling and user feedback throughout

## Extending Functionality
- Add new business logic in `business_analyzer.py`
- Add new file types in `rag.py`
- Add new chart/insight methods and they will appear in the PDF automatically

## Requirements
- Python 3.8+
- See `requirements.txt` for all Python dependencies

## License
MIT License

---

**Developed by [Your Name/Team]**