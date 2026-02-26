import requests
import json

api_key = 'app-MX4zcpz7unrWnUzVqD4MifOi'
base_url = 'http://localhost/v1'

headers = {
    'Authorization': f"Bearer {api_key}",
    'Content-Type': 'application/json'
}

payload = {
    "inputs": {},
    "query": "Hello",
    "response_mode": "blocking",
    "conversation_id": "72100e7c-9182-4fbe-b810-107d55c6a7d9",
    "user": "test_user_script"
}

try:
    print(f"Sending request to {base_url}/chat-messages...")
    response = requests.post(
        f"{base_url}/chat-messages",
        headers=headers,
        json=payload,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response JSON: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response Text: {response.text}")

except Exception as e:
    print(f"Error: {e}")
