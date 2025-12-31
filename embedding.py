import faiss
import numpy as np
import os
import pickle
import requests
from utils import get_gemini_api_key

class FaissIndex:
    def __init__(self, dim, index_path='faiss.index', meta_path='faiss_meta.pkl'):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        if os.path.exists(index_path) and os.path.exists(meta_path):
            self.index = faiss.read_index(index_path)
            with open(meta_path, 'rb') as f:
                self.meta = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.meta = []

    @staticmethod
    def load_or_create(dim, index_path='faiss.index', meta_path='faiss_meta.pkl'):
        if os.path.exists(index_path) and os.path.exists(meta_path):
            return FaissIndex(dim, index_path, meta_path)
        else:
            return FaissIndex(dim, index_path, meta_path)

    def add(self, embeddings, metas):
        self.index.add(np.array(embeddings).astype('float32'))
        self.meta.extend(metas)
        self.save()

    def search(self, embedding, top_k=5):
        D, I = self.index.search(np.array([embedding]).astype('float32'), top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.meta):
                results.append(self.meta[idx])
        return results

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'wb') as f:
            pickle.dump(self.meta, f)

# Gemini Embedding API (simulate, as official endpoint may differ)
def get_gemini_embedding(text: str) -> np.ndarray:
    api_key = get_gemini_api_key()
    url = 'https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key=' + api_key
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "models/embedding-001",
        "content": {"parts": [{"text": text}]}
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    embedding = response.json()['embedding']['values']
    return np.array(embedding)