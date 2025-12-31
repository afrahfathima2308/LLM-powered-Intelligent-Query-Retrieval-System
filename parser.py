import fitz  # PyMuPDF
import docx
from mailparser import parse_from_file
import os
from typing import List, Dict

def parse_pdf(file_path: str) -> List[Dict]:
    doc = fitz.open(file_path)
    results = []
    for page_num, page in enumerate(doc, 1):
        text = page.get_text('blocks')
        for i, block in enumerate(text):
            if block[4].strip():
                results.append({
                    'text': block[4].strip(),
                    'clause_id': f"{os.path.basename(file_path)}_p{page_num}_b{i}",
                    'page': page_num,
                    'file': os.path.basename(file_path)
                })
    return results

def parse_docx(file_path: str) -> List[Dict]:
    doc = docx.Document(file_path)
    results = []
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip():
            results.append({
                'text': para.text.strip(),
                'clause_id': f"{os.path.basename(file_path)}_para{i}",
                'page': None,
                'file': os.path.basename(file_path)
            })
    return results

def parse_eml(file_path: str) -> List[Dict]:
    mail = parse_from_file(file_path)
    body = mail.body or ''
    results = []
    for i, para in enumerate(body.split('\n\n')):
        if para.strip():
            results.append({
                'text': para.strip(),
                'clause_id': f"{os.path.basename(file_path)}_eml{i}",
                'page': None,
                'file': os.path.basename(file_path)
            })
    return results

def parse_file(file_path: str) -> List[Dict]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return parse_pdf(file_path)
    elif ext == '.docx':
        return parse_docx(file_path)
    elif ext == '.eml':
        return parse_eml(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")