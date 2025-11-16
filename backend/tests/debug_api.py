import requests
import json

# Test the API and show detailed errors
url = "http://localhost:8000/api/chat"

payload = {
    "message": "I need to schedule an appointment",
    "session_id": "test-debug"
}

print("Testing API endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("-" * 50)

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✓ Success!")
        data = response.json()
        print(f"Session ID: {data['session_id']}")
        print(f"\nMessages ({len(data['messages'])}):")
        for i, msg in enumerate(data['messages'], 1):
            print(f"{i}. {msg}")
    else:
        print(f"\n✗ Error {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n✗ Cannot connect to server")
    print("Make sure the server is running:")
    print("  uvicorn api.main:app --reload")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
