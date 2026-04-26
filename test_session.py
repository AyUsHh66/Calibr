import requests
import json

def test_create_session():
    url = "http://localhost:8000/api/sessions"
    payload = {
        "jd": "Senior React developer with TypeScript",
        "resume": "3 years React, basic TypeScript"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Session ID: {data.get('session_id')}")
        
        # Test GET session
        get_url = f"http://localhost:8000/api/sessions/{data.get('session_id')}"
        get_resp = requests.get(get_url)
        print(f"GET Status: {get_resp.status_code}")
        print(f"GET Data keys: {get_resp.json().keys()}")
        if 'chat_history' in get_resp.json():
            print("SUCCESS: chat_history found in response")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_session()
