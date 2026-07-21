"""Sprint 30 — seeds real customers/complaints into Postgres via the live
backend API so the Complaint Cases / Customers pages have genuine
demo-quality rows instead of the frontend's old hardcoded MOCK_CASES
fallback. Run against a running `docker compose up` stack:

    python scripts/seed_demo_cases.py
"""

import uuid

import requests

API_URL = "http://localhost:8000/api/v1"

CUSTOMERS = [
    {"full_name": "Mohammed Al Hinai", "email": "mohammed.hinai@example.com", "segment": "individual"},
    {"full_name": "Fatima Al Lawati", "email": "fatima.lawati@example.com", "segment": "individual"},
    {"full_name": "Sultan Al Khalidi", "email": "sultan.khalidi@example.com", "segment": "individual"},
    {"full_name": "Aisha Al Raisi", "email": "aisha.raisi@example.com", "segment": "individual"},
    {"full_name": "Hamed Al Balushi", "email": "hamed.balushi@example.com", "segment": "sme"},
    {"full_name": "Salma Al Maqbali", "email": "salma.maqbali@example.com", "segment": "individual"},
    {"full_name": "Yousef Al Harthy", "email": "yousef.harthy@example.com", "segment": "individual"},
    {"full_name": "Maryam Al Farsi", "email": "maryam.farsi@example.com", "segment": "sme"},
]

COMPLAINTS = [
    {"title": "Delayed Claim Processing for Muscat Accident", "category": "claims", "priority": "high", "severity": "high", "channel": "email", "product": "motor", "description": "Claim CLM-2024-812 has been pending for over 2 weeks with no update.", "policy_number": "POL-99281-22", "claim_number": "CLM-2024-812"},
    {"title": "Medical reimbursement denied wrongly", "category": "claims", "priority": "medium", "severity": "medium", "channel": "web_form", "product": "medical", "description": "Hospital visit reimbursement rejected despite policy covering it.", "policy_number": "POL-11234-23"},
    {"title": "Premium overcharged on renewal", "category": "billing", "priority": "high", "severity": "high", "channel": "whatsapp", "product": "motor", "description": "Renewal premium is 30% higher than quoted with no explanation."},
    {"title": "Unable to update contact details", "category": "service", "priority": "low", "severity": "low", "channel": "web_chat", "product": "medical", "description": "Portal rejects mobile number update with a generic error."},
    {"title": "Policy document not received after purchase", "category": "policy", "priority": "medium", "severity": "medium", "channel": "email", "product": "travel", "description": "Purchased travel policy 5 days ago, no documents in inbox."},
    {"title": "App crashes when filing a claim", "category": "technical", "priority": "medium", "severity": "low", "channel": "web_chat", "product": "motor", "description": "Mobile app crashes at the photo-upload step of claim filing."},
    {"title": "Repeated calls not resolving billing dispute", "category": "billing", "priority": "critical", "severity": "critical", "channel": "voice", "product": "medical", "description": "Third call this month about the same duplicate charge."},
    {"title": "Garage refusing cashless claim authorization", "category": "claims", "priority": "high", "severity": "high", "channel": "whatsapp", "product": "motor", "description": "Approved garage says authorization was never received."},
    {"title": "Incorrect beneficiary listed on life policy", "category": "policy", "priority": "high", "severity": "medium", "channel": "email", "product": "life", "description": "Beneficiary name has a typo that needs urgent correction."},
    {"title": "Refund for cancelled travel policy delayed", "category": "billing", "priority": "medium", "severity": "medium", "channel": "web_form", "product": "travel", "description": "Cancelled within cooling-off period, refund still not processed."},
    {"title": "SMS OTP not arriving for portal login", "category": "technical", "priority": "low", "severity": "low", "channel": "web_chat", "product": "medical", "description": "Cannot log in to customer portal, OTP never arrives."},
    {"title": "Dispute over claim settlement amount", "category": "claims", "priority": "critical", "severity": "critical", "channel": "voice", "product": "motor", "description": "Settlement offer is far below the garage repair estimate."},
]


def main() -> None:
    login = requests.post(
        f"{API_URL}/auth/login", json={"email": "admin@gmail.com", "password": "Admin@123"}
    )
    login.raise_for_status()
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    customer_ids = []
    for c in CUSTOMERS:
        resp = requests.post(
            f"{API_URL}/customers",
            json={
                "external_ref": f"demo-{uuid.uuid4().hex[:10]}",
                "full_name": c["full_name"],
                "email": c["email"],
                "customer_type": "active",
                "segment": c["segment"],
            },
        )
        if resp.status_code >= 400:
            print(f"customer create failed: {resp.status_code} {resp.text}")
            continue
        customer_ids.append(resp.json()["data"]["id"])
        print(f"customer created: {c['full_name']}")

    if not customer_ids:
        print("no customers created, aborting complaint seeding")
        return

    complaint_ids = []
    for i, comp in enumerate(COMPLAINTS):
        payload = {**comp, "customer_id": customer_ids[i % len(customer_ids)]}
        resp = requests.post(f"{API_URL}/complaints", json=payload, headers=headers)
        if resp.status_code >= 400:
            print(f"complaint create failed: {resp.status_code} {resp.text}")
            continue
        complaint_id = resp.json()["data"]["id"]
        complaint_ids.append(complaint_id)
        print(f"complaint created: {comp['title']}")

    # Vary status so every Complaint Cases tab has real rows.
    transitions = (
        [None] * 3          # stays "submitted" (New)
        + ["acknowledge"] * 2
        + ["escalate"] * 2
        + ["resolve"] * 3
        + ["close"] * 2
    )
    for complaint_id, action in zip(complaint_ids, transitions):
        if action is None:
            continue
        resp = requests.post(f"{API_URL}/complaints/{complaint_id}/{action}", headers=headers)
        print(f"{action} -> {complaint_id}: {resp.status_code}")

    print(f"\nSeeded {len(customer_ids)} customers and {len(complaint_ids)} complaints.")


if __name__ == "__main__":
    main()
