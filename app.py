import streamlit as st
import tempfile
import os
from parser import parse_file
from embedding import FaissIndex, get_gemini_embedding
from utils import format_json_response
import requests

# --- Custom CSS for hackathon-winning look ---
st.markdown('''
    <style>
    body {
        background: linear-gradient(135deg, #e0e7ff 0%, #f0f4ff 100%) !important;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .lexiq-logo {
        animation: spin 3s linear infinite;
        height: 70px;
        margin-bottom: 0.5em;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .answer-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(79,139,249,0.10);
        padding: 28px 32px;
        margin-bottom: 1.5em;
        border-left: 6px solid #4F8BF9;
    }
    .clause-card {
        background: #f7faff;
        border-radius: 10px;
        border-left: 4px solid #4F8BF9;
        margin-bottom: 12px;
        padding: 14px 18px;
        font-size: 1.05em;
        display: flex;
        align-items: flex-start;
    }
    .clause-icon {
        font-size: 1.5em;
        margin-right: 10px;
        color: #4F8BF9;
    }
    .chat-bubble {
        background: #eaf4ff;
        border-radius: 18px 18px 4px 18px;
        padding: 18px 22px;
        margin-bottom: 1em;
        color: #222;
        font-size: 1.1em;
        box-shadow: 0 2px 8px rgba(79,139,249,0.07);
    }
    .stButton>button {
        background: linear-gradient(90deg, #4F8BF9 0%, #6dd5ed 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1em;
        padding: 0.6em 2em;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        box-shadow: 0 2px 8px rgba(79,139,249,0.10);
        transition: background 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #6dd5ed 0%, #4F8BF9 100%);
    }
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.97em;
        margin-top: 2em;
    }
    </style>
''', unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.image("https://img.icons8.com/fluency/96/ai.png", width=70, output_format="auto", caption="<div class='lexiq-logo'></div>", use_column_width=False)
st.sidebar.title("LexIQ")
st.sidebar.markdown("""
**LLM-powered Query–Retrieval System**

- Upload PDFs, DOCX, or EML files
- Ask questions and get contextual answers
- Powered by Google Gemini & FAISS

---
Made for insurance, legal, HR, and compliance
""")
if st.sidebar.button("Clear All"):
    st.session_state.clear()
    st.experimental_rerun()

# --- Main Title ---
st.markdown("""
<h1 style='text-align: center; color: #4F8BF9; margin-bottom: 0;'>
    <img src='https://img.icons8.com/fluency/96/ai.png' class='lexiq-logo' style='vertical-align:middle;'> LexIQ
</h1>
<p style='text-align: center; color: #666; margin-top: 0;'>LLM-powered Intelligent Query–Retrieval System</p>
<hr style='border: 1px solid #4F8BF9;'>
""", unsafe_allow_html=True)

# --- File Upload UI ---
st.markdown("### 1. Upload Documents", unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Upload PDF, DOCX, or EML files",
    type=["pdf", "docx", "eml"],
    accept_multiple_files=True,
    help="You can upload multiple files at once."
)

# --- Indexing with Progress Bar ---
if uploaded_files:
    with st.spinner("Parsing and indexing documents..."):
        progress = st.progress(0, text="Indexing documents...")
        total_files = len(uploaded_files)
        for idx, uploaded_file in enumerate(uploaded_files):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            clauses = parse_file(tmp_path)
            embeddings = []
            for clause in clauses:
                emb = get_gemini_embedding(clause['text'])
                embeddings.append(emb)
            if embeddings:
                if 'index' not in st.session_state:
                    st.session_state['index'] = FaissIndex(dim=len(embeddings[0]))
                st.session_state['index'].add(embeddings, clauses)
            os.remove(tmp_path)
            progress.progress((idx + 1) / total_files, text=f"Indexed {idx + 1} of {total_files} files")
        progress.empty()
    st.success("Documents indexed!")

# --- Query Input as Chat Bubble ---
st.markdown("### 2. Ask a Question", unsafe_allow_html=True)
with st.form(key="query_form"):
    query = st.text_input(
        "Type your question about the uploaded documents:",
        placeholder="e.g. How many days does the breaching party have to cure the breach?"
    )
    submit_query = st.form_submit_button("Ask")

# --- Results Layout ---
if submit_query and query:
    with st.spinner("Retrieving answer from Gemini..."):
        query_emb = get_gemini_embedding(query)
        index = st.session_state.get('index', None)
        if index is None:
            st.error("No documents indexed yet. Please upload and index documents first.")
        else:
            relevant_clauses = index.search(query_emb, top_k=5)
            context = "\n\n".join([c['text'] for c in relevant_clauses])
            prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer with rationale and cite relevant clauses."
            api_key = os.getenv('GEMINI_API_KEY')
            url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=' + api_key
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 512}
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            answer = response.json()['candidates'][0]['content']['parts'][0]['text']
            rationale = answer
            json_response = {
                "query": query,
                "answer": answer,
                "relevant_clauses": [
                    {
                        "text": c['text'],
                        "clause_id": c['clause_id'],
                        "page": c['page'],
                        "file": c['file']
                    } for c in relevant_clauses
                ],
                "confidence_score": None,
                "rationale": rationale
            }
            # --- Chat Bubble for User Query ---
            st.markdown(f"<div class='chat-bubble'><b>You:</b> {query}</div>", unsafe_allow_html=True)
            # --- Animated Answer Card ---
            st.markdown(f"<div class='answer-card'><b>LexIQ:</b><br>{answer}</div>", unsafe_allow_html=True)
            # --- Clause Highlights with Icons ---
            st.markdown("<h5 style='margin-top:2em;'>Relevant Clauses</h5>", unsafe_allow_html=True)
            for c in relevant_clauses:
                st.markdown(f"""
                    <div class='clause-card'>
                        <span class='clause-icon'>📄</span>
                        <div>
                            <b>{c['file']}</b> <span style='color:#888;'>(Page: {c['page']}, ID: {c['clause_id']})</span><br>
                            <span style='color:#333;'>{c['text']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            # --- JSON Output ---
            with st.expander("Show raw JSON response"):
                st.code(format_json_response(json_response), language="json")

# --- Footer ---
st.markdown("""
<hr style='border: 1px solid #eee;'>
<div class='footer'>
    <b>&copy; 2024 LexIQ</b> &mdash; Powered by Streamlit, Gemini, and FAISS | Designed for Hackathons 🚀
</div>
""", unsafe_allow_html=True)