# Copyright 2026 Google LLC
# Seed script for AI Dev Team tasks
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-bcd65a0ed380"

db = firestore.Client(project=PROJECT_ID)

SAMPLE_TASKS = [
    {
        "id": "TASK-101",
        "title": "Define User Stories for Payment Gateway",
        "role": "PM",
        "status": "Done",
        "priority": "High",
        "description": "Specify customer checkout flow and Stripe webhook acceptance criteria.",
        "deliverable": "PRD document ready in specs/payment_v1.md",
    },
    {
        "id": "TASK-102",
        "title": "Design Mobile Checkout UI Mockup",
        "role": "Designer",
        "status": "In Progress",
        "priority": "High",
        "description": "Create modern mobile UI wireframe with payment method cards and dark mode.",
        "deliverable": "Visual mockup to be generated.",
    },
    {
        "id": "TASK-103",
        "title": "Implement Webhook Verification Handler",
        "role": "Developer",
        "status": "In Progress",
        "priority": "High",
        "description": "Implement HMAC SHA256 signature verification for inbound payment events.",
        "deliverable": "Python handler logic in payment_service.py",
    },
    {
        "id": "TASK-104",
        "title": "Automated Unit Tests for Currency Formatting",
        "role": "QA",
        "status": "Backlog",
        "priority": "Medium",
        "description": "Write test cases for edge cases with multi-currency decimals and rounding.",
        "deliverable": "Pytest suite in tests/test_currency.py",
    },
    {
        "id": "TASK-105",
        "title": "Sprint Velocity & Bug Defect Ratio Analysis",
        "role": "Analyst",
        "status": "Backlog",
        "priority": "Medium",
        "description": "Calculate story points completed per sprint and defect density metrics.",
        "deliverable": "Metrics summary report.",
    },
]

def seed():
    print(f"Seeding tasks into Firestore project '{PROJECT_ID}'...")
    collection_ref = db.collection("tasks")
    for task in SAMPLE_TASKS:
        collection_ref.document(task["id"]).set(task)
        print(f"Seeded {task['id']}: [{task['role']}] {task['title']}")
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed()
