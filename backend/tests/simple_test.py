"""
Simple test script to verify the healthcare API is working
Run this while the server is already running
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/api/chat"

def test_chat():
    payload = {
        "message": "I have a headache and feel dizzy",
        "session_id": "test-session-123"
    }
    
    print("Sending request to:", API_URL)
    print("Payload:", json.dumps(payload, indent=2))
    print("\nWaiting for response...\n")
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✓ Response received!")
        print("\nSession ID:", result.get("session_id"))
        print("\nAssistant Messages:")
        print("=" * 60)
        for msg in result.get("messages", []):
            print(msg)
        print("=" * 60)
            
    except requests.exceptions.RequestException as e:
        print("✗ Error:", e)
        if hasattr(e, 'response') and e.response is not None:
            print("Response:", e.response.text)

if __name__ == "__main__":
    test_chat()
