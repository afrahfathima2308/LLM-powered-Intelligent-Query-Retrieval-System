import requests
import json

# Base URL for the webhook API
BASE_URL = "http://localhost:8000"

def upload_documents(file_paths):
    """
    Upload documents to the webhook API
    """
    files = []
    for file_path in file_paths:
        with open(file_path, 'rb') as f:
            files.append(('files', (file_path.split('/')[-1], f.read(), 'application/octet-stream')))
    
    response = requests.post(f"{BASE_URL}/upload", files=files)
    return response.json()

def ask_question(question):
    """
    Ask a question via the webhook API
    """
    data = {'question': question}
    response = requests.post(f"{BASE_URL}/query", data=data)
    return response.json()

def get_status():
    """
    Get the current status of indexed documents
    """
    response = requests.get(f"{BASE_URL}/status")
    return response.json()

def clear_index():
    """
    Clear all indexed documents
    """
    response = requests.delete(f"{BASE_URL}/clear")
    return response.json()

def health_check():
    """
    Check if the API is healthy
    """
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

# Example usage
if __name__ == "__main__":
    print("=== LexIQ Webhook API Client Example ===\n")
    
    # 1. Health check
    print("1. Health check:")
    health = health_check()
    print(json.dumps(health, indent=2))
    print()
    
    # 2. Upload documents (replace with your file paths)
    print("2. Upload documents:")
    # file_paths = ["test.txt", "sample.pdf"]  # Replace with your files
    # upload_result = upload_documents(file_paths)
    # print(json.dumps(upload_result, indent=2))
    print("(Uncomment and add your file paths to test upload)")
    print()
    
    # 3. Check status
    print("3. Check status:")
    status = get_status()
    print(json.dumps(status, indent=2))
    print()
    
    # 4. Ask a question (only works if documents are uploaded)
    print("4. Ask a question:")
    # question = "How many days does the breaching party have to cure the breach?"
    # answer = ask_question(question)
    # print(json.dumps(answer, indent=2))
    print("(Uncomment and add your question to test query)")
    print()
    
    print("=== API Endpoints ===")
    print("POST /upload - Upload and index documents")
    print("POST /query - Ask a question")
    print("GET /status - Get current status")
    print("GET /health - Health check")
    print("DELETE /clear - Clear all indexed documents")
    print()
    print("To start the API server, run: python webhook_api.py") 