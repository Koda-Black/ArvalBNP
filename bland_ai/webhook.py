"""
Webhook handler for Bland AI call events.
Receives real-time updates during and after calls.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Data storage
DATA_DIR = Path(__file__).parent.parent / "data"


def save_call_data(call_id: str, data: Dict[str, Any]) -> None:
    """Save call data to file."""
    DATA_DIR.mkdir(exist_ok=True)
    calls_file = DATA_DIR / "calls.json"
    
    calls = []
    if calls_file.exists():
        with open(calls_file, "r") as f:
            calls = json.load(f)
    
    # Update or add call
    existing = next((c for c in calls if c.get("call_id") == call_id), None)
    if existing:
        existing.update(data)
    else:
        calls.append(data)
    
    with open(calls_file, "w") as f:
        json.dump(calls, f, indent=2, default=str)


def process_call_started(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process call started event."""
    call_id = data.get("call_id")
    logger.info(f"Call started: {call_id}")
    
    call_data = {
        "call_id": call_id,
        "status": "in_progress",
        "started_at": datetime.now().isoformat(),
        "phone_number": data.get("to"),
        "from_number": data.get("from"),
    }
    
    save_call_data(call_id, call_data)
    return {"status": "acknowledged", "call_id": call_id}


def process_call_ended(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process call ended event."""
    call_id = data.get("call_id")
    logger.info(f"Call ended: {call_id}")
    
    call_data = {
        "call_id": call_id,
        "status": "completed",
        "ended_at": datetime.now().isoformat(),
        "duration": data.get("duration"),
        "transcript": data.get("transcript"),
        "recording_url": data.get("recording_url"),
        "summary": data.get("summary"),
        "analysis": data.get("analysis"),
    }
    
    save_call_data(call_id, call_data)
    
    # Extract any leads or appointments from analysis
    analysis = data.get("analysis", {})
    if analysis:
        process_call_analysis(call_id, analysis)
    
    return {"status": "processed", "call_id": call_id}


def process_call_analysis(call_id: str, analysis: Dict[str, Any]) -> None:
    """Process call analysis to extract leads and appointments."""
    # Extract customer info
    customer_name = analysis.get("customer_name")
    customer_phone = analysis.get("customer_phone")
    customer_email = analysis.get("customer_email")
    
    # Check for lead capture
    if analysis.get("is_lead"):
        lead_data = {
            "call_id": call_id,
            "contact_name": customer_name,
            "contact_phone": customer_phone,
            "contact_email": customer_email,
            "company_name": analysis.get("company_name"),
            "fleet_size": analysis.get("fleet_size"),
            "interests": analysis.get("interests"),
            "created_at": datetime.now().isoformat(),
            "source": "Bland AI Call",
        }
        
        leads_file = DATA_DIR / "leads.json"
        leads = []
        if leads_file.exists():
            with open(leads_file, "r") as f:
                leads = json.load(f)
        leads.append(lead_data)
        with open(leads_file, "w") as f:
            json.dump(leads, f, indent=2)
        
        logger.info(f"Lead captured from call {call_id}")
    
    # Check for appointments
    if analysis.get("appointment_booked"):
        apt_data = {
            "call_id": call_id,
            "customer_name": customer_name,
            "appointment_type": analysis.get("appointment_type"),
            "date": analysis.get("appointment_date"),
            "time": analysis.get("appointment_time"),
            "created_at": datetime.now().isoformat(),
            "source": "Bland AI Call",
        }
        
        appointments_file = DATA_DIR / "appointments.json"
        appointments = []
        if appointments_file.exists():
            with open(appointments_file, "r") as f:
                appointments = json.load(f)
        appointments.append(apt_data)
        with open(appointments_file, "w") as f:
            json.dump(appointments, f, indent=2)
        
        logger.info(f"Appointment booked from call {call_id}")


def handle_webhook(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main webhook handler for Bland AI events.
    
    Args:
        event_type: Type of event (call.started, call.ended, etc.)
        data: Event data from Bland AI
        
    Returns:
        Response to send back to Bland AI
    """
    handlers = {
        "call.started": process_call_started,
        "call.ended": process_call_ended,
        "call.analyzed": lambda d: process_call_analysis(d.get("call_id"), d),
    }
    
    handler = handlers.get(event_type)
    if handler:
        return handler(data)
    
    logger.warning(f"Unknown event type: {event_type}")
    return {"status": "unknown_event"}


# Example Flask/FastAPI webhook endpoint
WEBHOOK_EXAMPLE = '''
# Flask example:
from flask import Flask, request, jsonify
from bland_ai.webhook import handle_webhook

app = Flask(__name__)

@app.route("/webhook/bland-ai", methods=["POST"])
def bland_ai_webhook():
    data = request.json
    event_type = data.get("event")
    result = handle_webhook(event_type, data)
    return jsonify(result)

# FastAPI example:
from fastapi import FastAPI, Request
from bland_ai.webhook import handle_webhook

app = FastAPI()

@app.post("/webhook/bland-ai")
async def bland_ai_webhook(request: Request):
    data = await request.json()
    event_type = data.get("event")
    result = handle_webhook(event_type, data)
    return result
'''
