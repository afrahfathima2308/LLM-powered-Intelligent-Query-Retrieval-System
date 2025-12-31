from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import json
from typing import List, Optional
import uvicorn
from parser import parse_file
from embedding import FaissIndex, get_gemini_embedding
from utils import get_gemini_api_key
import requests

app = FastAPI(title="LexIQ Webhook API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for the FAISS index
global_index = None

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and index documents (PDF, DOCX, EML)
    """
    global global_index
    
    try:
        uploaded_files = []
        for file in files:
            if file.filename.lower().endswith(('.pdf', '.docx', '.eml')):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                    content = await file.read()
                    tmp.write(content)
                    tmp_path = tmp.name
                
                # Parse the file
                clauses = parse_file(tmp_path)
                embeddings = []
                
                for clause in clauses:
                    emb = get_gemini_embedding(clause['text'])
                    embeddings.append(emb)
                
                if embeddings:
                    if global_index is None:
                        global_index = FaissIndex(dim=len(embeddings[0]))
                    global_index.add(embeddings, clauses)
                
                uploaded_files.append(file.filename)
                os.remove(tmp_path)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Successfully indexed {len(uploaded_files)} documents",
            "files": uploaded_files
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@app.post("/query")
async def ask_question(question: str = Form(...)):
    """
    Ask a question about the uploaded documents
    """
    global global_index
    
    if global_index is None:
        raise HTTPException(status_code=400, detail="No documents indexed. Please upload documents first.")
    
    try:
        # Get query embedding
        query_emb = get_gemini_embedding(question)
        
        # Search for relevant clauses
        relevant_clauses = global_index.search(query_emb, top_k=5)
        
        if not relevant_clauses:
            return JSONResponse({
                "query": question,
                "answer": "No relevant information found in the uploaded documents.",
                "relevant_clauses": [],
                "confidence_score": None,
                "rationale": "No matching clauses found."
            })
        
        # Compose prompt for Gemini
        context = "\n\n".join([c['text'] for c in relevant_clauses])
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer with rationale and cite relevant clauses."
        
        # Call Gemini for answer
        api_key = get_gemini_api_key()
        url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=' + api_key
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 512}
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        answer = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        # Compose response
        result = {
            "query": question,
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
            "rationale": answer
        }
        
        return JSONResponse(result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "LexIQ Webhook API"}

@app.get("/status")
async def get_status():
    """
    Get current status (number of indexed documents)
    """
    global global_index
    
    if global_index is None:
        return {"indexed_documents": 0, "total_clauses": 0}
    else:
        return {
            "indexed_documents": len(set([meta['file'] for meta in global_index.meta])),
            "total_clauses": len(global_index.meta)
        }

@app.delete("/clear")
async def clear_index():
    """
    Clear all indexed documents
    """
    global global_index
    global_index = None
    return {"status": "success", "message": "Index cleared successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 