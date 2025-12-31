import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_gemini_api_key():
    return os.getenv('GEMINI_API_KEY')

def format_json_response(response_dict):
    return json.dumps(response_dict, indent=2, ensure_ascii=False)