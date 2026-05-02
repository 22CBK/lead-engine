import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')

api_key = os.environ.get('GROQ_API_KEY')
endpoint = 'https://api.groq.com/openai/v1/chat/completions'
model = 'llama-3.1-8b-instant'

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": model,
    "response_format": {"type": "json_object"},
    "messages": [
        {"role": "system", "content": "You are a helpful sales AI. You MUST respond with ONLY a valid JSON object."},
        {"role": "user", "content": "Return a JSON object with key 'test' and value 'success'."}
    ],
    "temperature": 0.3
}

response = requests.post(endpoint, headers=headers, json=payload)
print(response.status_code)
print(response.text)
