import requests
import json
import uuid

API_URL = "http://localhost:8000/api/v1/complaints"
CUSTOMER_ID = "44e231b1-2e6b-4e89-a2a2-4a0b349d9b60"

complaints = [
    {
        "customer_id": CUSTOMER_ID,
        "title": "Delayed Claim Processing for Muscat Accident",
        "category": "claims",
        "product": "motor",
        "priority": "high",
        "severity": "major",
        "source": "email",
        "description": "I submitted a claim for a car accident in Muscat over 2 weeks ago (Claim CLM-2024-812). It is still pending and no one is replying to my emails. I need this resolved urgently as my car is stuck in the garage.",
        "policy_number": "POL-99281-22",
        "claim_number": "CLM-2024-812",
        "channel": "email"
    },
    {
        "customer_id": CUSTOMER_ID,
        "title": "Medical reimbursement denied wrongly",
        "category": "claims",
        "product": "medical",
        "priority": "medium",
        "severity": "moderate",
        "source": "web_form",
        "description": "My recent visit to Badr Al Samaa Hospital was rejected for reimbursement. The policy clearly states dental emergencies are covered up to 500 OMR. Please review this decision.",
        "policy_number": "POL-11234-23",
        "channel": "web_form"
    }
]

for c in complaints:
    res = requests.post(API_URL, json=c)
    print(f"Created complaint: {res.status_code} - {res.text}")
