# LexIQ: LLM-powered Intelligent Query–Retrieval System

LexIQ is a Streamlit web app that enables contextual question-answering over large documents (PDF, DOCX, EML) using Google Gemini 1.5 Flash and FAISS.

## Features
- Upload and parse PDFs, DOCX, and email files
- Extracts and indexes document sections/clauses
- Semantic search using Gemini embeddings and FAISS
- Natural language query interface
- Cites relevant clauses with metadata
- JSON output with rationale and confidence

## Setup
1. Clone this repo and `cd` into the folder
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your Gemini API key to a `.env` file:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage
- Upload one or more documents (PDF, DOCX, EML)
- Enter a natural language question
- View the answer, relevant clauses, and JSON output

## Tech Stack
- Python, Streamlit, FAISS, Google Gemini 1.5 Flash, PyMuPDF, python-docx, mail-parser