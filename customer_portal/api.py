#!/usr/bin/env python3
"""
Customer Portal API

This provides a secure way for customers to access their own data
without giving them access to your Vapi dashboard.

Features:
- View call transcripts for their assistant only
- View appointments booked through their agent
- View leads captured
- View analytics (call volume, duration, etc.)
"""

import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Voice Agent Customer Portal",
    description="Access call transcripts, appointments, and analytics for your voice agent",
    version="1.0.0"
)

# CORS for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
VAPI_API_KEY = os.getenv("VAPI_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")

# Customer database (in production, use a real database)
CUSTOMERS = {
    "arval": {
        "api_key": "arval_api_key_here",
        "assistant_id": "b543468c-e12e-481f-abb6-d0e129c7e5bb",
        "company_name": "Arval BNP Paribas",
        "phone_numbers": ["+14087312213"]
    }
    # Add more customers here
}


# Models
class CallRecord(BaseModel):
    id: str
    started_at: str
    ended_at: Optional[str]
    duration_seconds: Optional[int]
    caller_phone: Optional[str]
    transcript: Optional[str]
    summary: Optional[str]
    status: str


class Appointment(BaseModel):
    id: str
    customer_name: str
    contact_phone: str
    contact_email: str
    appointment_type: str
    preferred_date: str
    preferred_time: str
    vehicle_registration: Optional[str]
    status: str
    created_at: str


class Lead(BaseModel):
    id: str
    contact_name: str
    contact_email: str
    contact_phone: str
    company_name: Optional[str]
    vehicle_interests: Optional[str]
    created_at: str


class Analytics(BaseModel):
    total_calls: int
    total_duration_minutes: int
    average_call_duration_seconds: int
    calls_today: int
    calls_this_week: int
    calls_this_month: int
    appointments_booked: int
    leads_captured: int


# Authentication
async def verify_customer(x_api_key: str = Header(...)) -> Dict:
    """Verify customer API key and return their config."""
    for customer_id, config in CUSTOMERS.items():
        if config["api_key"] == x_api_key:
            return {"customer_id": customer_id, **config}
    raise HTTPException(status_code=401, detail="Invalid API key")


# Vapi API Helper
async def fetch_vapi_calls(assistant_id: str, limit: int = 100) -> List[Dict]:
    """Fetch calls from Vapi for a specific assistant."""
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.vapi.ai/call?assistantId={assistant_id}&limit={limit}"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return []


# Endpoints
@app.get("/")
async def root():
    return {
        "service": "Voice Agent Customer Portal",
        "version": "1.0.0",
        "endpoints": [
            "/calls",
            "/calls/{call_id}",
            "/appointments",
            "/leads",
            "/analytics"
        ]
    }


@app.get("/calls", response_model=List[CallRecord])
async def get_calls(
    customer: Dict = Depends(verify_customer),
    limit: int = 50,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get all calls for the customer's assistant.
    
    - **limit**: Maximum number of calls to return (default: 50)
    - **start_date**: Filter calls after this date (YYYY-MM-DD)
    - **end_date**: Filter calls before this date (YYYY-MM-DD)
    """
    calls = await fetch_vapi_calls(customer["assistant_id"], limit)
    
    results = []
    for call in calls:
        # Calculate duration
        duration = None
        if call.get("startedAt") and call.get("endedAt"):
            start = datetime.fromisoformat(call["startedAt"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(call["endedAt"].replace("Z", "+00:00"))
            duration = int((end - start).total_seconds())
        
        results.append(CallRecord(
            id=call.get("id", ""),
            started_at=call.get("startedAt", ""),
            ended_at=call.get("endedAt"),
            duration_seconds=duration,
            caller_phone=call.get("customer", {}).get("number"),
            transcript=call.get("transcript"),
            summary=call.get("summary"),
            status=call.get("status", "unknown")
        ))
    
    return results


@app.get("/calls/{call_id}")
async def get_call_detail(
    call_id: str,
    customer: Dict = Depends(verify_customer)
):
    """Get detailed information about a specific call including full transcript."""
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.vapi.ai/call/{call_id}"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                call = await response.json()
                # Verify this call belongs to the customer's assistant
                if call.get("assistantId") != customer["assistant_id"]:
                    raise HTTPException(status_code=403, detail="Access denied")
                return call
            raise HTTPException(status_code=404, detail="Call not found")


@app.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    customer: Dict = Depends(verify_customer),
    status: Optional[str] = None
):
    """
    Get all appointments booked through the voice agent.
    
    In production, this would query your appointments database.
    For now, this extracts appointments from call tool calls.
    """
    # In production: query your database
    # For demo: return sample data
    return [
        Appointment(
            id="apt_001",
            customer_name="John Smith",
            contact_phone="+44 7700 900000",
            contact_email="john@example.com",
            appointment_type="MOT",
            preferred_date="2026-01-15",
            preferred_time="Morning (9-12)",
            vehicle_registration="AB12 CDE",
            status="confirmed",
            created_at="2026-01-07T10:30:00Z"
        )
    ]


@app.get("/leads", response_model=List[Lead])
async def get_leads(
    customer: Dict = Depends(verify_customer)
):
    """
    Get all leads captured through the voice agent.
    
    In production, this would query your leads database.
    """
    # In production: query your database
    return []


@app.get("/analytics", response_model=Analytics)
async def get_analytics(
    customer: Dict = Depends(verify_customer),
    period: str = "month"  # day, week, month, year
):
    """
    Get analytics for the voice agent.
    
    - **period**: Time period for analytics (day, week, month, year)
    """
    calls = await fetch_vapi_calls(customer["assistant_id"], 1000)
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)
    
    total_duration = 0
    calls_today = 0
    calls_this_week = 0
    calls_this_month = 0
    
    for call in calls:
        started_at = call.get("startedAt")
        if started_at:
            call_time = datetime.fromisoformat(started_at.replace("Z", "+00:00")).replace(tzinfo=None)
            
            if call_time >= today_start:
                calls_today += 1
            if call_time >= week_start:
                calls_this_week += 1
            if call_time >= month_start:
                calls_this_month += 1
        
        # Calculate duration
        if call.get("startedAt") and call.get("endedAt"):
            start = datetime.fromisoformat(call["startedAt"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(call["endedAt"].replace("Z", "+00:00"))
            total_duration += int((end - start).total_seconds())
    
    avg_duration = total_duration // len(calls) if calls else 0
    
    return Analytics(
        total_calls=len(calls),
        total_duration_minutes=total_duration // 60,
        average_call_duration_seconds=avg_duration,
        calls_today=calls_today,
        calls_this_week=calls_this_week,
        calls_this_month=calls_this_month,
        appointments_booked=0,  # Query from database
        leads_captured=0  # Query from database
    )


@app.get("/export/calls")
async def export_calls(
    customer: Dict = Depends(verify_customer),
    format: str = "json"  # json or csv
):
    """Export all calls as JSON or CSV for compliance/archival."""
    calls = await fetch_vapi_calls(customer["assistant_id"], 10000)
    
    if format == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Started", "Ended", "Duration", "Caller", "Status"])
        for call in calls:
            writer.writerow([
                call.get("id"),
                call.get("startedAt"),
                call.get("endedAt"),
                call.get("duration"),
                call.get("customer", {}).get("number"),
                call.get("status")
            ])
        return {"content": output.getvalue(), "format": "csv"}
    
    return {"calls": calls, "format": "json"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
