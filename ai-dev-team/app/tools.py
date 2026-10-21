# Copyright 2026 Google LLC
# Firestore tools for AI Dev Team Agent
import uuid
import logging
from typing import List, Dict, Any, Optional
import google.auth
from google.auth.transport.requests import Request
import httpx

PROJECT_ID = "qwiklabs-gcp-04-bcd65a0ed380"
FIRESTORE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/tasks"

# In-memory fail-safe state initialized with sprint tasks
IN_MEMORY_TASKS: Dict[str, Dict[str, Any]] = {
    "TASK-101": {
        "id": "TASK-101",
        "title": "Define User Stories for Payment Gateway",
        "role": "PM",
        "status": "Done",
        "priority": "High",
        "description": "Specify customer checkout flow and Stripe webhook acceptance criteria.",
        "deliverable": "PRD document ready in specs/payment_v1.md"
    },
    "TASK-102": {
        "id": "TASK-102",
        "title": "Design Mobile Checkout UI Mockup",
        "role": "Designer",
        "status": "In Progress",
        "priority": "High",
        "description": "Create modern mobile UI wireframe with payment method cards and dark mode.",
        "deliverable": "Visual mockup to be generated."
    },
    "TASK-103": {
        "id": "TASK-103",
        "title": "Implement Webhook Verification Handler",
        "role": "Developer",
        "status": "In Progress",
        "priority": "High",
        "description": "Implement HMAC SHA256 signature verification for inbound payment events.",
        "deliverable": "Python handler logic in payment_service.py"
    },
    "TASK-104": {
        "id": "TASK-104",
        "title": "Automated Unit Tests for Currency Formatting",
        "role": "QA",
        "status": "Backlog",
        "priority": "Medium",
        "description": "Write pytest suites covering USD, EUR, and IDR currency decimal parsing.",
        "deliverable": "tests/test_currency.py"
    },
    "TASK-105": {
        "id": "TASK-105",
        "title": "Sprint Velocity & Bug Defect Ratio Analysis",
        "role": "Analyst",
        "status": "Backlog",
        "priority": "Medium",
        "description": "Evaluate historical sprint burndown and compute expected team cycle times.",
        "deliverable": "reports/velocity_sprint_12.json"
    },
    "TASK-1CD8": {
        "id": "TASK-1CD8",
        "title": "Implement JWT Auth",
        "role": "Developer",
        "status": "Done",
        "priority": "High",
        "description": "Add JWT verification and refresh token handling.",
        "deliverable": "auth/jwt_handler.py"
    }
}

def _get_headers() -> Dict[str, str]:
    """Retrieve OAuth2 access token with cloud-platform and datastore scopes."""
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/datastore"]
    )
    if not creds.valid:
        creds.refresh(Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json"
    }

def _parse_firestore_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Firestore REST field representations to Python dict."""
    result = {}
    for key, val in fields.items():
        if "stringValue" in val:
            result[key] = val["stringValue"]
        elif "integerValue" in val:
            result[key] = int(val["integerValue"])
        elif "booleanValue" in val:
            result[key] = val["booleanValue"]
        elif "nullValue" in val:
            result[key] = None
        else:
            result[key] = list(val.values())[0] if val else ""
    return result

def _to_firestore_fields(task: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Python dict into Firestore REST format."""
    fields = {}
    for k, v in task.items():
        if isinstance(v, bool):
            fields[k] = {"booleanValue": v}
        elif isinstance(v, int):
            fields[k] = {"integerValue": str(v)}
        else:
            fields[k] = {"stringValue": str(v or "")}
    return {"fields": fields}

def list_tasks(role: Optional[str] = None) -> List[Dict[str, Any]]:
    """List software project tasks from the project board in Firestore.
    
    Args:
        role: Optional filter by team role ('PM', 'Designer', 'Developer', 'QA', 'Analyst').
              If omitted or empty, all tasks across all roles are returned.
    
    Returns:
        List of task dictionaries containing id, title, role, status, priority, and description.
    """
    try:
        headers = _get_headers()
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(FIRESTORE_BASE_URL, headers=headers)
            if resp.status_code == 200:
                raw_docs = resp.json().get("documents", [])
                tasks = []
                for doc in raw_docs:
                    fields = doc.get("fields", {})
                    task_data = _parse_firestore_fields(fields)
                    if task_data.get("id"):
                        IN_MEMORY_TASKS[task_data["id"]] = task_data
                        tasks.append(task_data)
                if tasks:
                    if role and role.strip():
                        return [t for t in tasks if t.get("role", "").lower() == role.strip().lower()]
                    return tasks
    except Exception as e:
        logging.warning("Firestore REST list_tasks failed (%s), using in-memory cache", e)

    # In-memory fallback
    all_tasks = list(IN_MEMORY_TASKS.values())
    if role and role.strip():
        return [t for t in all_tasks if t.get("role", "").lower() == role.strip().lower()]
    return all_tasks

def get_task(task_id: str) -> Dict[str, Any]:
    """Retrieve full details of a specific task by its ID.
    
    Args:
        task_id: Unique task identifier (e.g., 'TASK-101').
        
    Returns:
        Task details dictionary or an error message if not found.
    """
    clean_id = task_id.strip()
    try:
        headers = _get_headers()
        url = f"{FIRESTORE_BASE_URL}/{clean_id}"
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                task = _parse_firestore_fields(resp.json().get("fields", {}))
                IN_MEMORY_TASKS[clean_id] = task
                return task
    except Exception as e:
        logging.warning("Firestore REST get_task failed (%s), checking in-memory cache", e)

    if clean_id in IN_MEMORY_TASKS:
        return IN_MEMORY_TASKS[clean_id]
    return {"error": f"Task {clean_id} not found on the board."}

def create_task(title: str, role: str, description: str, priority: str = "Medium") -> Dict[str, Any]:
    """Create a new task on the project board and assign it to a team role.
    
    Args:
        title: Short title of the task.
        role: Team role assigned to the task ('PM', 'Designer', 'Developer', 'QA', 'Analyst').
        description: Detailed explanation of the requirements or objective.
        priority: Priority level ('High', 'Medium', 'Low').
        
    Returns:
        Confirmation dictionary with the created task ID and details.
    """
    task_id = f"TASK-{str(uuid.uuid4())[:4].upper()}"
    task_data = {
        "id": task_id,
        "title": title,
        "role": role,
        "status": "Backlog",
        "priority": priority,
        "description": description,
        "deliverable": "",
    }
    IN_MEMORY_TASKS[task_id] = task_data

    try:
        headers = _get_headers()
        url = f"{FIRESTORE_BASE_URL}/{task_id}"
        payload = _to_firestore_fields(task_data)
        with httpx.Client(timeout=8.0) as client:
            resp = client.patch(url, headers=headers, json=payload)
            if resp.status_code == 200:
                task_data = _parse_firestore_fields(resp.json().get("fields", {}))
                IN_MEMORY_TASKS[task_id] = task_data
    except Exception as e:
        logging.warning("Firestore REST create_task sync failed (%s), saved in-memory", e)

    return {"message": f"Task {task_id} created successfully.", "task": task_data}

def update_task_status(task_id: str, status: str, deliverable: str = "") -> Dict[str, Any]:
    """Update the status and deliverable notes of a task.
    
    Args:
        task_id: Unique task identifier (e.g., 'TASK-101').
        status: New status ('Backlog', 'In Progress', 'In Review', 'Done').
        deliverable: Optional summary or link of what was delivered/completed.
        
    Returns:
        Status update confirmation dictionary.
    """
    clean_id = task_id.strip()
    current = IN_MEMORY_TASKS.get(clean_id, {"id": clean_id, "title": "Updated Task", "role": "Developer"})
    current["status"] = status
    if deliverable:
        current["deliverable"] = deliverable
    IN_MEMORY_TASKS[clean_id] = current

    try:
        headers = _get_headers()
        url = f"{FIRESTORE_BASE_URL}/{clean_id}"
        payload = _to_firestore_fields(current)
        with httpx.Client(timeout=8.0) as client:
            resp = client.patch(url, headers=headers, json=payload)
            if resp.status_code == 200:
                updated = _parse_firestore_fields(resp.json().get("fields", {}))
                IN_MEMORY_TASKS[clean_id] = updated
    except Exception as e:
        logging.warning("Firestore REST update_task_status sync failed (%s), updated in-memory", e)

    return {"message": f"Task {clean_id} updated to status '{status}'.", "task": current}
