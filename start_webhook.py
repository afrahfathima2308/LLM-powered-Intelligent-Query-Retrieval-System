import subprocess
import sys
import time
import requests
from pyngrok import ngrok

def start_webhook_with_ngrok():
    """
    Start the webhook API server and expose it with ngrok
    """
    print("🚀 Starting LexIQ Webhook API...")
    
    try:
        # Start the API server in background
        print("Starting FastAPI server on localhost:8000...")
        api_process = subprocess.Popen([sys.executable, "webhook_api.py"])
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test if server is running
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ API server is running on http://localhost:8000")
            else:
                print("❌ API server failed to start")
                return
        except:
            print("❌ API server failed to start")
            return
        
        # Expose with ngrok
        print("🌐 Exposing with ngrok...")
        public_url = ngrok.connect(8000)
        print(f"✅ Your webhook URL: {public_url}")
        print(f"📋 Health check: {public_url}/health")
        print(f"📊 Status: {public_url}/status")
        print("\n📝 Example usage:")
        print(f"curl -X POST {public_url}/query -d 'question=How many days does the breaching party have to cure the breach?'")
        
        print("\n🔄 Press Ctrl+C to stop the server")
        
        try:
            api_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            api_process.terminate()
            ngrok.kill()
            print("✅ Server stopped")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have installed: pip install pyngrok")

def start_webhook_local():
    """
    Start the webhook API server locally only
    """
    print("🚀 Starting LexIQ Webhook API on localhost...")
    print("📋 Your webhook URL: http://localhost:8000")
    print("📊 Health check: http://localhost:8000/health")
    print("🔄 Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "webhook_api.py"])
    except KeyboardInterrupt:
        print("\n✅ Server stopped")

if __name__ == "__main__":
    print("LexIQ Webhook API Starter")
    print("=" * 30)
    
    choice = input("Choose option:\n1. Start locally only\n2. Start with ngrok (expose to internet)\nEnter choice (1 or 2): ")
    
    if choice == "2":
        try:
            import pyngrok
            start_webhook_with_ngrok()
        except ImportError:
            print("❌ pyngrok not installed. Install with: pip install pyngrok")
            print("Starting locally instead...")
            start_webhook_local()
    else:
        start_webhook_local() 