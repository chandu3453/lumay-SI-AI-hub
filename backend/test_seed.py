import requests

API_URL = "http://localhost:8000/api/v1/complaints"

payload = {
    "title": "Test Title",
    "description": "Test Description",
    "category": "general",
    "product": "motor",
    "priority": "medium",
    "source": "web_form",
    "policy_number": "",
    "claim_number": ""
}

res = requests.post(API_URL, json=payload)
print(f"Status: {res.status_code}")
print(f"Body: {res.text}")
