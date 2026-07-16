"""Synthetic Data Generator — creates realistic demo datasets."""

from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from app.platform.logging import get_logger
from domains.interaction.constants.interaction_constants import InteractionChannel, InteractionDirection, InteractionStatus

logger = get_logger(__name__)

FIRST_NAMES = ["Fatima", "Ahmed", "Sara", "Mohammed", "Aisha", "Khalid", "Layla", "Omar", "Noora", "Yusuf", "Mariam", "Hassan", "Amira", "Abdullah", "Zainab", "Rashid", "Hiba", "Saeed", "Nadia", "Salim"]
LAST_NAMES = ["Al Lawati", "Al Balushi", "Al Hinai", "Al Riyami", "Al Busaidi", "Al Said", "Al Wahaibi", "Al Mahrooqi", "Al Farsi", "Al Zakwani", "Al Habsi", "Al Shukri", "Al Qasimi", "Al Junaibi", "Al Abri", "Al Hasani", "Al Rashi", "Al Kharusi", "Al Shibli", "Al Shamsi"]
CITIES = ["Muscat", "Salalah", "Sohar", "Nizwa", "Sur", "Ibri", "Barka", "Rustaq", "Ibri", "Seeb"]
STATES = ["OM-MU", "OM-SH", "OM-BA", "OM-DA", "OM-SS", "OM-ZA", "OM-BU", "OM-DA", "OM-ZA", "OM-MU"]
STREETS = ["Sultan Qaboos St", "Al Khuwair St", "Qurum St", "Al Murtifaa St", "Al Ghubra St", "Bawshar St", "Al Hail St", "Al Ansab St", "Al Seeb St", "Al Amarat St"]
COMPANY_NAMES = ["Oman Tech Solutions LLC", "Muscat Trading Co", "Salalah Logistics LLC", "Al Khaleej Construction", "Sohar Shipping Co", "Nizwa Medical Supplies", "Sur Fishing Co", "Ibri Agriculture LLC", "Barka Real Estate", "Rustaq Dairy Products"]
COMPLAINT_CATEGORIES = ["billing", "claims", "policy", "service", "technical", "general"]
COMPLAINT_PRIORITIES = ["low", "medium", "high", "critical"]
COMPLAINT_SEVERITIES = ["minor", "moderate", "major", "critical"]
COMPLAINT_STATUSES = ["submitted", "under_review", "investigating", "escalated", "resolved", "closed", "archived"]
COMPLAINT_SOURCES = ["phone", "email", "web_form", "chat", "social_media"]
INTERACTION_CHANNELS = ["email", "whatsapp", "voice", "web_form"]
INTERACTION_DIRECTIONS = ["inbound", "outbound"]
INTERACTION_STATUSES = ["received", "processed", "completed"]
WORKFLOW_STATUSES = ["pending", "active", "completed", "cancelled", "archived"]
WORKFLOW_STAGES = ["initiated", "queued", "assigned", "in_progress", "review", "approval", "resolution", "completed"]
SLA_STATUSES = ["within_sla", "at_risk", "breached"]
TEAMS = ["claims", "billing", "service", "underwriting", "compliance"]
NOTIFICATION_CHANNELS = ["email", "sms", "whatsapp", "in_app"]
NOTIFICATION_TYPES = ["alert", "reminder", "confirmation", "status_update", "escalation", "resolution"]
NOTIFICATION_STATUSES = ["pending", "queued", "sent", "delivered", "failed"]
CUSTOMER_SEGMENTS = ["individual", "corporate", "sme", "vip"]

COMPLAINT_TITLES = [
    "Overcharged on motor insurance premium",
    "Medical claim denied without explanation",
    "Rude customer service at Al Khuwair branch",
    "Travel policy cancellation without notice",
    "Incorrect billing on comprehensive policy",
    "Delayed motor claim processing - 3 weeks waiting",
    "Misleading coverage for home insurance",
    "Unauthorized charges on auto-renew policy",
    "Difficulty reaching claims department by phone",
    "Wrong policy applied to new vehicle purchase",
]

COMPLAINT_DESCRIPTIONS = [
    "My comprehensive motor insurance premium increased from OMR 450 to OMR 580 without any prior notification. No one at the call center could explain the increase.",
    "My medical claim for surgery at Badr Al Sama Hospital was denied after 4 weeks. The reason was 'pre-existing condition' but my policy covers this.",
    "The customer service representative at the Al Khuwair branch was unhelpful. I waited 45 minutes only to be told to call the call center.",
    "My travel gold policy was cancelled due to a missed payment that was actually deducted from my bank account. The automatic payment had been working for 3 years.",
    "I was billed OMR 320 for my policy instead of the agreed OMR 250. I have emails confirming the original rate of OMR 250 per month.",
    "It has been over 3 weeks since I filed my motor accident claim and no resolution. Every time I call, they say it is under surveyor review.",
    "The agent told me I had comprehensive coverage but when I filed a claim after a minor accident, I found out many things were not covered.",
    "There are charges on my policy that I never authorized. I have called three times and no one has addressed this.",
    "I have been transferred between departments 5 times. The automated system keeps routing me in circles without reaching a real person.",
    "They applied my payment to the wrong policy number ending in 789 instead of my policy ending in 456. Now I am showing overdue.",
]

BILLING_CONTEXTS = ["monthly premium", "deductible", "copay", "fee", "surcharge", "late fee", "policy installment"]
CLAIMS_CONTEXTS = ["auto accident", "home damage", "medical procedure", "property loss", "liability claim", "fire damage", "flood damage", "theft"]
RETAIL_NAMES = ["Toyota Corolla", "Nissan Patrol", "BMW X5", "Mercedes C200", "Hyundai Tucson", "Mitsubishi Pajero", "Ford Ranger", "Kia Cerato", "Honda Accord", "Chevrolet Tahoe"]
HOSPITAL_NAMES = ["Badr Al Sama Hospital", "Khoula Hospital", "Sultan Qaboos Hospital", "Starcare Hospital", "Muscat Private Hospital", "Nizwa Hospital", "Sohar Hospital", "Al Nahdha Hospital"]
GARAGE_NAMES = ["Al Futtaim Auto Center", "Zahran Garage", "Muscat Car Care", "Oman Auto Service", "Ghala Auto Workshop", "European Car Care", "Al Seeb Auto Center", "Modern Auto Garage"]


class SyntheticStore:
    def __init__(self) -> None:
        self._data: dict[str, list[dict[str, Any]]] = {}

    def set(self, key: str, items: list[dict[str, Any]]) -> None:
        self._data[key] = items

    def get(self, key: str, default: list | None = None) -> list[dict[str, Any]]:
        return self._data.get(key, default or [])

    def clear(self) -> None:
        self._data.clear()

    def size(self) -> dict[str, int]:
        return {k: len(v) for k, v in self._data.items()}


_store: SyntheticStore | None = None


def get_synthetic_store() -> SyntheticStore:
    global _store
    if _store is None:
        _store = SyntheticStore()
    return _store


def reset_synthetic_store() -> None:
    global _store
    _store = None


def generate_synthetic_data() -> SyntheticStore:
    store = get_synthetic_store()
    store.clear()
    random.seed(42)

    now = datetime.now(timezone.utc)

    customers = _generate_customers(500)
    interactions = _generate_interactions(1500, customers, now)
    complaints = _generate_complaints(800, customers, interactions, now)
    workflows = _generate_workflows(800, complaints, now)
    notifications = _generate_notifications(800, workflows, complaints, customers, now)

    store.set("customers", customers)
    store.set("interactions", interactions)
    store.set("complaints", complaints)
    store.set("workflows", workflows)
    store.set("notifications", notifications)

    logger.info(
        "synthetic_data_generated",
        customers=len(customers),
        interactions=len(interactions),
        complaints=len(complaints),
        workflows=len(workflows),
        notifications=len(notifications),
    )
    return store


def _random_date(now: datetime, max_days_ago: int) -> str:
    days = random.randint(0, max_days_ago)
    hours = random.randint(0, 23)
    dt = now - timedelta(days=days, hours=hours)
    return dt.isoformat()


def _generate_customers(count: int) -> list[dict[str, Any]]:
    customers = []
    for i in range(count):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        city_idx = random.randint(0, len(CITIES) - 1)
        segment = random.choice(CUSTOMER_SEGMENTS)
        email_domain = random.choice(["gmail.com", "hotmail.com", "omantel.net.om", "outlook.com", "live.com"])
        customers.append({
            "id": str(uuid.uuid4()),
            "customer_number": f"CUST-{i+1:05d}",
            "external_ref": f"EXT-{random.randint(10000, 99999)}",
            "full_name": f"{first} {last}",
            "email": f"{first.lower()}.{last.lower()}@{email_domain}",
            "mobile_number": f"+968{random.choice(['91','92','93','94','95','96','97','98','99'])}{random.randint(100000, 999999):06d}",
            "segment": segment,
            "company_name": random.choice(COMPANY_NAMES) if segment == "corporate" else None,
            "status": random.choices(["active", "inactive", "suspended"], weights=[80, 15, 5])[0],
            "city": CITIES[city_idx],
            "state": STATES[city_idx],
            "created_at": _random_date(datetime.now(timezone.utc), 365),
            "nationality": random.choice(["Omani", "Omani", "Omani", "Indian", "Bangladeshi", "Filipino", "Egyptian"]),
        })
    return customers


SCENARIOS = [
    {
        "subject": "Motor claim delay",
        "category": "claims",
        "messages": [
            {"role": "user", "content": "I filed my motor claim CLM-2025-09921 three weeks ago and still haven't heard back.", "timestamp": "time_1"},
            {"role": "assistant", "content": "I apologize for the delay. Let me check the status of claim CLM-9921 for your Motor Insurance policy. It seems it is pending surveyor review.", "timestamp": "time_2"},
            {"role": "user", "content": "Can you please speed it up? I need my car repaired.", "timestamp": "time_3"},
            {"role": "assistant", "content": "I will flag this as urgent for the surveyor. We should get an update in 24 hours.", "timestamp": "time_4"}
        ]
    },
    {
        "subject": "Medical reimbursement",
        "category": "claims",
        "messages": [
            {"role": "user", "content": "My hospital visit was rejected for reimbursement. Why was it denied?", "timestamp": "time_1"},
            {"role": "assistant", "content": "I understand your concern. Let me check the pre-authorization details. It appears the provider was outside our network.", "timestamp": "time_2"},
            {"role": "user", "content": "But it was an emergency!", "timestamp": "time_3"},
            {"role": "assistant", "content": "For emergencies, out-of-network visits are covered. Please submit the emergency admission certificate for review.", "timestamp": "time_4"}
        ]
    },
    {
        "subject": "Travel policy cancellation",
        "category": "policy",
        "messages": [
            {"role": "user", "content": "I need to cancel my travel policy because my trip was cancelled. Can I get a refund?", "timestamp": "time_1"},
            {"role": "assistant", "content": "I can help with that. Since your travel policy has not started yet, you are eligible for a full refund minus a minor processing fee.", "timestamp": "time_2"}
        ]
    },
    {
        "subject": "Home insurance damage",
        "category": "claims",
        "messages": [
            {"role": "user", "content": "A pipe burst in my basement and there is water damage. How do I file a claim?", "timestamp": "time_1"},
            {"role": "assistant", "content": "I am sorry to hear that. Please take photos of the damage immediately to document it, and secure the leak. I will initiate claim CLM-HOME-991 for you.", "timestamp": "time_2"}
        ]
    },
    {
        "subject": "Renewal reminder",
        "category": "policy",
        "messages": [
            {"role": "user", "content": "I received a renewal reminder but my premium increased by 30%. Why?", "timestamp": "time_1"},
            {"role": "assistant", "content": "Let me look at your policy renewal terms. The increase is due to the claims filed last year, which affected your no-claim discount.", "timestamp": "time_2"}
        ]
    },
    {
        "subject": "Payment refund",
        "category": "billing",
        "messages": [
            {"role": "user", "content": "I was double charged for my monthly premium payment. I need a refund.", "timestamp": "time_1"},
            {"role": "assistant", "content": "I apologize for the billing error. I have processed the refund for the duplicate charge of OMR 120. It should show up in 3 business days.", "timestamp": "time_2"}
        ]
    },
    {
        "subject": "Garage complaint",
        "category": "service",
        "messages": [
            {"role": "user", "content": "The authorized garage did a terrible repair job on my front bumper. It is still loose.", "timestamp": "time_1"},
            {"role": "assistant", "content": "That is unacceptable. We hold our network garages to high standards. Please return to the garage, and I will notify the quality team.", "timestamp": "time_2"}
        ]
    },
    {
        "subject": "Provider complaint",
        "category": "service",
        "messages": [
            {"role": "user", "content": "The dental clinic refused to accept my insurance card, saying they don't cover it anymore.", "timestamp": "time_1"},
            {"role": "assistant", "content": "I apologize for the confusion. Our network agreement with that clinic is still active. I will contact their billing department.", "timestamp": "time_2"}
        ]
    },
    {
        "subject": "Business insurance claim",
        "category": "claims",
        "messages": [
            {"role": "user", "content": "We had a fire at our retail store. We need to submit a business interruption claim.", "timestamp": "time_1"},
            {"role": "assistant", "content": "I am very sorry to hear that. I will transfer this to our Commercial Claims team immediately. They will guide you through the asset evaluation.", "timestamp": "time_2"}
        ]
    }
]


def _generate_interactions(count: int, customers: list[dict[str, Any]], now: datetime) -> list[dict[str, Any]]:
    interactions = []
    # 1. Generate structured conversations
    for i in range(120):
        customer = customers[i % len(customers)]
        scenario = SCENARIOS[i % len(SCENARIOS)]
        
        t1 = (now - timedelta(days=random.randint(1, 30))).isoformat()
        t2 = (datetime.fromisoformat(t1) + timedelta(minutes=5)).isoformat()
        t3 = (datetime.fromisoformat(t1) + timedelta(minutes=10)).isoformat()
        t4 = (datetime.fromisoformat(t1) + timedelta(minutes=12)).isoformat()
        
        formatted_messages = []
        for msg in scenario["messages"]:
            content = msg["content"]
            role = msg["role"]
            if "time_1" in msg["timestamp"]:
                ts = t1
            elif "time_2" in msg["timestamp"]:
                ts = t2
            elif "time_3" in msg["timestamp"]:
                ts = t3
            else:
                ts = t4
            formatted_messages.append({"role": role, "content": content, "timestamp": ts})
            
        # Balanced channel assignment across the 4 key customer communication channels
        channel = [
            InteractionChannel.WHATSAPP,
            InteractionChannel.WEB_FORM,
            InteractionChannel.EMAIL,
            InteractionChannel.VOICE,
        ][i % 4]

        interactions.append({
            "id": str(uuid.uuid4()),
            "customer_id": customer["id"],
            "channel": channel,
            "direction": InteractionDirection.INBOUND,
            "subject": scenario["subject"],
            "transcript": json.dumps(formatted_messages),
            "status": InteractionStatus.RECEIVED,
            "created_at": t1,
        })
        
    # 2. Generate the rest (randomly)
    for _ in range(count - 120):
        customer = random.choice(customers)
        interactions.append({
            "id": str(uuid.uuid4()),
            "customer_id": customer["id"],
            "channel": random.choice([InteractionChannel.EMAIL, InteractionChannel.VOICE, InteractionChannel.WHATSAPP, InteractionChannel.WEB_FORM]),
            "direction": random.choice([InteractionDirection.INBOUND, InteractionDirection.OUTBOUND]),
            "subject": random.choice(COMPLAINT_TITLES),
            "transcript": random.choice(COMPLAINT_DESCRIPTIONS),
            "status": random.choice([InteractionStatus.RECEIVED, InteractionStatus.COMPLETED]),
            "created_at": _random_date(now, 180),
        })
    return sorted(interactions, key=lambda x: x["created_at"], reverse=True)


def _generate_complaints(count: int, customers: list[dict[str, Any]], interactions: list[dict[str, Any]], now: datetime) -> list[dict[str, Any]]:
    sentiments = ["positive", "negative", "neutral", "mixed"]
    sent_weights = [5, 55, 25, 15]
    complaints = []
    
    # 1. Explicitly link complaints for our structured conversations
    for i in range(100):
        interaction = interactions[i]
        customer = next((c for c in customers if c["id"] == interaction["customer_id"]), None)
        if not customer:
            customer = random.choice(customers)
            
        category = "general"
        subject = interaction["subject"]
        if "claim" in subject.lower() or "damage" in subject.lower() or "reimbursement" in subject.lower():
            category = "claims"
        elif "premium" in subject.lower() or "refund" in subject.lower() or "price" in subject.lower() or "pricing" in subject.lower():
            category = "billing"
        elif "policy" in subject.lower() or "renewal" in subject.lower():
            category = "policy"
        elif "garage" in subject.lower() or "provider" in subject.lower():
            category = "service"
            
        try:
            msgs = json.loads(interaction["transcript"])
            desc = msgs[0]["content"]
        except (json.JSONDecodeError, KeyError, IndexError):
            desc = interaction["transcript"]
            
        policy_number = f"POL-{random.randint(2024, 2026)}-{random.randint(10000, 99999):05d}"
        [first_name, last_name] = customer["full_name"].split(" ", 1) if " " in customer["full_name"] else [customer["full_name"], "User"]
        complaints.append({
            "id": str(uuid.uuid4()),
            "complaint_number": f"LUM-{datetime.now(timezone.utc).year}-{i+1:05d}",
            "customer_id": customer["id"],
            "interaction_id": interaction["id"],
            "title": f"Complaint: {subject}",
            "description": desc,
            "category": category,
            "subcategory": random.choice(CLAIMS_CONTEXTS) if category == "claims" else random.choice(BILLING_CONTEXTS),
            "priority": "high" if "delay" in subject.lower() or "damage" in subject.lower() else "medium",
            "severity": "major" if "damage" in subject.lower() or "fire" in subject.lower() else "moderate",
            "status": "under_review",
            "source": "chat" if interaction["channel"] == InteractionChannel.WEB_FORM else str(interaction["channel"].value),
            "assigned_queue": category if category != "policy" else "service",
            "policy_number": policy_number,
            "insurance_line": random.choice(["motor", "medical", "travel", "home", "life", "business"]),
            "metadata": {
                "ai_sentiment": "negative",
                "ai_sentiment_polarity": -0.6,
                "ai_theme": f"{category} dispute",
            },
            "created_at": interaction["created_at"],
        })
        
    # 2. Generate the rest (700) randomly
    for i in range(count - 100):
        customer = random.choice(customers)
        interaction = random.choice(interactions)
        category = random.choice(COMPLAINT_CATEGORIES)
        severity = random.choices(COMPLAINT_SEVERITIES, weights=[25, 40, 25, 10])[0]
        priority = random.choices(COMPLAINT_PRIORITIES, weights=[15, 35, 35, 15])[0]
        status = random.choices(COMPLAINT_STATUSES, weights=[10, 15, 15, 5, 25, 20, 10])[0]
        sentiment = random.choices(sentiments, weights=sent_weights)[0]
        polarity = {"positive": 0.6, "negative": -0.7, "neutral": 0.0, "mixed": 0.1}[sentiment]
        title_idx = i % len(COMPLAINT_TITLES)
        insurance_line = random.choice(["motor", "medical", "travel", "home", "life", "business"])
        policy_number = f"POL-{random.randint(2024, 2026)}-{random.randint(10000, 99999):05d}"
        complaints.append({
            "id": str(uuid.uuid4()),
            "complaint_number": f"LUM-{datetime.now(timezone.utc).year}-{100+i+1:05d}",
            "customer_id": customer["id"],
            "interaction_id": interaction["id"],
            "title": COMPLAINT_TITLES[title_idx],
            "description": COMPLAINT_DESCRIPTIONS[title_idx],
            "category": category,
            "subcategory": random.choice(BILLING_CONTEXTS) if category == "billing" else random.choice(CLAIMS_CONTEXTS),
            "priority": priority,
            "severity": severity,
            "status": status,
            "source": random.choice(COMPLAINT_SOURCES),
            "assigned_queue": random.choice(TEAMS) if status not in ("resolved", "closed", "archived") else None,
            "policy_number": policy_number,
            "insurance_line": insurance_line,
            "metadata": {
                "ai_sentiment": sentiment,
                "ai_sentiment_polarity": polarity,
                "ai_theme": random.choice(["billing issue", "claim dispute", "service quality", "policy confusion", "technical problem"]),
            },
            "created_at": _random_date(now, 120),
        })
    return complaints


def _generate_workflows(count: int, complaints: list[dict[str, Any]], now: datetime) -> list[dict[str, Any]]:
    workflows = []
    for i, complaint in enumerate(complaints[:count]):
        status = random.choices(WORKFLOW_STATUSES, weights=[15, 30, 35, 10, 10])[0]
        stage = random.choice(WORKFLOW_STAGES)
        sla = random.choices(SLA_STATUSES, weights=[60, 25, 15])[0]
        started = _random_date(now, 60)
        completed = None
        if status == "completed":
            started_dt = datetime.fromisoformat(started)
            completed_dt = started_dt + timedelta(hours=random.randint(4, 168))
            completed = completed_dt.isoformat()
        workflows.append({
            "id": str(uuid.uuid4()),
            "workflow_number": f"WF-{i+1:05d}",
            "complaint_id": complaint["id"],
            "assigned_team": random.choice(TEAMS),
            "assigned_agent_id": str(uuid.uuid4()),
            "workflow_status": status,
            "workflow_stage": stage,
            "priority": complaint["priority"],
            "sla_status": sla,
            "started_at": started,
            "completed_at": completed,
            "created_at": started,
        })
    return workflows


def _generate_notifications(count: int, workflows: list[dict[str, Any]], complaints: list[dict[str, Any]], customers: list[dict[str, Any]], now: datetime) -> list[dict[str, Any]]:
    notifications = []
    for i in range(count):
        wf = random.choice(workflows)
        complaint = random.choice(complaints)
        ch = random.choice(NOTIFICATION_CHANNELS)
        status = random.choices(NOTIFICATION_STATUSES, weights=[10, 15, 10, 45, 20])[0]
        recipient = random.choice(customers)
        notifications.append({
            "id": str(uuid.uuid4()),
            "notification_number": f"NOTIF-{i+1:05d}",
            "workflow_id": wf["id"],
            "complaint_id": complaint["id"],
            "notification_type": random.choice(NOTIFICATION_TYPES),
            "notification_channel": ch,
            "recipient": recipient.get("email", f"customer{i}@email.com"),
            "subject": f"Update: {random.choice(COMPLAINT_TITLES)}",
            "message": f"Your complaint has been {random.choice(['updated', 'reviewed', 'escalated', 'resolved'])}.",
            "notification_status": status,
            "priority": random.choice(["low", "medium", "high"]),
            "retry_count": random.randint(0, 2),
            "created_at": _random_date(now, 30),
        })
    return notifications