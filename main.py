import uuid
import streamlit as st
from agents import ExtractionAgent, SummarizationAgent, ChatAgent
from vectordb import VectorDB, DB_PATH
from rag import RAG
import tempfile
import sqlite3
import os

st.set_page_config(page_title="RAG Gemini Dashboard", layout="wide")
st.title("📊 RAG Dashboard with Gemini API")

st.markdown("""
<style>
    .session-info {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 0.75em 1em;
        margin-bottom: 1em;
        font-size: 1em;
        color: #333;
        border: 1px solid #e0e0e0;
    }
    .file-info {
        color: #1a73e8;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

if 'vectordb' not in st.session_state:
    st.session_state.vectordb = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

uploaded_file = st.file_uploader("Upload your document (PDF, DOC/DOCX, XLS/XLSX, CSV)", type=["xlsx", "xls", "csv", "pdf", "doc", "docx"])

# Directory to save uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store session/thread in DB if not already
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('SELECT * FROM sessions WHERE session_id=?', (st.session_state.session_id,))
if not c.fetchone():
    c.execute('INSERT INTO sessions (session_id, thread_id, file_name) VALUES (?, ?, ?)',
              (st.session_state.session_id, st.session_state.thread_id, uploaded_file.name if uploaded_file else None))
    conn.commit()
conn.close()

st.markdown(f"""
<div class="session-info">
    <b>Session ID:</b> <code>{st.session_state.session_id}</code><br>
    <b>Thread ID:</b> <code>{st.session_state.thread_id}</code><br>
    <b>File:</b> <span class="file-info">{uploaded_file.name if uploaded_file else 'No file uploaded yet'}</span>
</div>
""", unsafe_allow_html=True)

if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    # Save file only if it doesn't already exist
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    with st.spinner("Extracting and summarizing..."):
        extraction_agent = ExtractionAgent()
        summarization_agent = SummarizationAgent()
        rag = RAG()
        # Use the new method for all supported file types
        text = rag.extract_text_from_file(uploaded_file)
        st.session_state.extracted_text = text
        summary = summarization_agent.summarize(text)
        st.session_state.summary = summary
        # Chunk the document for better RAG retrieval
        chunk_size = 500  # characters per chunk
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        embeddings = [rag.embed(chunk) for chunk in chunks]
        vectordb = VectorDB(dim=len(embeddings[0]))
        vectordb.add(embeddings, chunks)
        st.session_state.vectordb = vectordb
    st.success(f"Document processed and stored in vectorDB! Session: {st.session_state.session_id}")
    st.subheader("Summary")
    st.write(st.session_state.summary)

if st.session_state.vectordb:
    st.subheader(f"Chat with your document (Session: {st.session_state.session_id})")
    user_query = st.text_input("Ask a question about your document:")
    if user_query:
        chat_agent = ChatAgent(st.session_state.vectordb, RAG())
        with st.spinner("Thinking..."):
            answer = chat_agent.chat(user_query)
        code_block = ChatAgent.extract_code_block(answer)
        if code_block:
            st.markdown("**Generated Chart:**")
            try:
                # Provide context for code execution
                local_vars = {"pd": __import__('pandas'), "plt": __import__('matplotlib.pyplot')}
                # If you want to provide the dataframe, you can add it to local_vars
                if st.session_state.extracted_text:
                    import pandas as pd
                    from io import StringIO
                    # Try to reconstruct DataFrame from extracted text if possible
                    try:
                        df = pd.read_csv(StringIO(st.session_state.extracted_text))
                        local_vars['df'] = df
                    except Exception:
                        pass
                exec(code_block, {}, local_vars)
                st.pyplot(local_vars['plt'])
            except Exception as e:
                st.error(f"Error executing generated code: {e}")
        else:
            st.markdown(f"**Answer:** {answer}")

# --- RAG Management Section ---
def get_rags():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rags (
        rag_id TEXT PRIMARY KEY,
        name TEXT,
        tags TEXT,
        category TEXT,
        session_id TEXT,
        thread_id TEXT,
        file_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('SELECT rag_id, name, tags, category, file_name FROM rags')
    rags = c.fetchall()
    conn.close()
    return rags

def add_rag(rag_id, name, tags, category, session_id, thread_id, file_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO rags (rag_id, name, tags, category, session_id, thread_id, file_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (rag_id, name, tags, category, session_id, thread_id, file_name))
    conn.commit()
    conn.close()

def update_rag(rag_id, name, tags, category):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE rags SET name=?, tags=?, category=? WHERE rag_id=?', (name, tags, category, rag_id))
    conn.commit()
    conn.close()

def delete_rag(rag_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM rags WHERE rag_id=?', (rag_id,))
    conn.commit()
    conn.close()

# --- UI for RAG Management ---
st.sidebar.header('🗂️ Manage RAGs')
rags = get_rags()
if rags:
    for rag in rags:
        rag_id, name, tags, category, file_name = rag
        with st.sidebar.expander(f"{name or 'Untitled RAG'} ({os.path.basename(file_name)})"):
            st.markdown(f"**Tags:** {tags or '-'}  ")
            st.markdown(f"**Category:** {category or '-'}  ")
            new_name = st.text_input(f"Edit Name for {rag_id}", value=name or '', key=f"name_{rag_id}")
            new_tags = st.text_input(f"Edit Tags for {rag_id}", value=tags or '', key=f"tags_{rag_id}")
            new_category = st.text_input(f"Edit Category for {rag_id}", value=category or '', key=f"cat_{rag_id}")
            # Horizontal layout for all four buttons using a single row, with unique keys
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4, gap="small")
            with btn_col1:
                if st.button("Save", key=f"save_{rag_id}"):
                    update_rag(rag_id, new_name, new_tags, new_category)
                    st.success("Updated Successfully!")
                    st.rerun()
            with btn_col2:
                if st.button("Delete", key=f"delete_{rag_id}"):
                    delete_rag(rag_id)
                    st.warning("Deleted Successfully!")
                    st.rerun()
            with btn_col3:
                if st.button("Download", key=f"download_{rag_id}"):
                    import base64
                    try:
                        with open(file_name, "rb") as f:
                            data = f.read()
                        b64 = base64.b64encode(data).decode()
                        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_name)}">Click here to download</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception:
                        st.error("File not found on server.")
            with btn_col4:
                if st.button("Preview", key=f"preview_{rag_id}"):
                    try:
                        import pandas as pd
                        df = None
                        if file_name.endswith('.csv'):
                            df = pd.read_csv(file_name)
                        elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                            df = pd.read_excel(file_name)
                        if df is not None:
                            st.dataframe(df.head(20))
                        else:
                            st.info("Preview not supported for this file type.")
                    except Exception as e:
                        st.error(f"Preview failed: {e}")
else:
    st.sidebar.info('No RAGs found. Upload a document to create one.')

# --- Add RAG on file upload ---
if uploaded_file:
    rag_id = f"rag_{st.session_state.session_id}_{st.session_state.thread_id}_{uploaded_file.name}"
    # Only add if not already present (avoid duplicate RAGs for same file/session/thread)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT rag_id FROM rags WHERE rag_id=?', (rag_id,))
    if not c.fetchone():
        add_rag(rag_id, uploaded_file.name, '', '', st.session_state.session_id, st.session_state.thread_id, file_path)
    conn.close()
