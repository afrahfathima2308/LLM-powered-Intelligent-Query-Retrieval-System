import time
import requests
from pyngrok import ngrok
import subprocess
import sys
import threading

def start_webhook_server():
    """Start the webhook API server in background"""
    try:
        subprocess.run([sys.executable, "webhook_api.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start webhook server")

def generate_webhook_url():
    """Generate webhook URL using ngrok"""
    print("🚀 LexIQ Webhook URL Generator")
    print("=" * 40)
    
    # Start server in background
    print("📡 Starting webhook server...")
    server_thread = threading.Thread(target=start_webhook_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Webhook server is running on localhost:8000")
        else:
            print("❌ Server not responding properly")
            return None
    except:
        print("❌ Server failed to start")
        return None
    
    # Generate ngrok URL
    print("🔗 Creating ngrok tunnel...")
    try:
        public_url = ngrok.connect(8000)
        print(f"✅ Your webhook URL: {public_url}")
        print(f"📋 Health check: {public_url}/health")
        print(f"📊 Status: {public_url}/status")
        
        print("\n📝 Test commands:")
        print(f"curl {public_url}/health")
        print(f"curl -X POST {public_url}/query -d 'question=test'")
        
        print("\n🔄 Keep this terminal open to maintain the tunnel")
        print("Press Ctrl+C to stop")
        
        return public_url
        
    except Exception as e:
        print(f"❌ Error creating ngrok tunnel: {e}")
        print("💡 Make sure you have installed: pip install pyngrok")
        return None

if __name__ == "__main__":
    try:
        url = generate_webhook_url()
        if url:
            # Keep running
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping webhook server...")
        print("✅ Webhook URL generator stopped") 