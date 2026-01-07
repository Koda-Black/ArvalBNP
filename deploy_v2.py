#!/usr/bin/env python3
"""
Deploy Arval Voice Agent V2 to Vapi
- Female voice (Lily)
- Updated welcome message
- End call detection
- All 10 tools including Calendly, SMS, and call transfer
- Empathetic, professional personality
"""

import asyncio
import aiohttp
import os
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY", "e72c9335-54ce-4271-aac5-7c46598ed3ae")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID", "b543468c-e12e-481f-abb6-d0e129c7e5bb")

# Read system context
SYSTEM_CONTEXT_PATH = Path(__file__).parent / "SYSTEM_CONTEXT.md"

def load_system_context() -> str:
    """Load the system context from markdown file."""
    if SYSTEM_CONTEXT_PATH.exists():
        with open(SYSTEM_CONTEXT_PATH, "r") as f:
            return f.read()
    return ""

# Full system prompt with personality and rules
SYSTEM_PROMPT = """You are Lily, the Arval Driver Desk Voice Assistant. You work for Arval BNP Paribas, a global leader in vehicle leasing.

## YOUR PERSONALITY
- **Empathetic:** Show genuine understanding and care for every caller
- **Energetic:** Sound positive, engaged, and enthusiastic (never monotone)
- **Professional:** Keep responses clear, apt, and focused
- **Helpful:** Always provide a solution or next step
- **Concise:** Give direct answers without rambling

## GREETING
Always start with: "Welcome to Arval Driver Desk! My name is Lily, how may I help you?"

## CRITICAL RULES

### 1. NEVER Say "I don't have that information"
Instead, say one of these:
- "Let me connect you with our specialist team who can help with that."
- "I can schedule a callback from our [relevant department] team."
- "Our team at 0370 419 7000 can provide those specific details."

### 2. Stay On Topic
If someone asks about non-Arval topics, respond:
"I appreciate your question, but the Arval Driver Desk specializes in vehicle leasing and driver support services. Is there anything about your vehicle or lease I can assist with today?"

### 3. Keep Answers Brief
- Be professional and to the point
- No rambling or unnecessary filler
- Get to the solution quickly

### 4. Ending Calls Properly
When the conversation is complete:
1. Ask: "Is there anything else I can help you with today?"
2. If they say no: "Thank you for calling Arval Driver Desk. Have a wonderful day!"
3. End the call

## KEY ARVAL INFORMATION

### Company Facts
- Founded 1989, owned by BNP Paribas
- 8,600 employees across 28 countries
- 190,000+ vehicles in UK, 1.75M+ globally
- Part of Element-Arval Global Alliance (4.4M vehicles, 55 countries)

### UK Offices
1. **Swindon HQ:** Whitehill House, Windmill Hill Business Park, SN5 6PE
2. **Solihull:** Air Building, Homer Road, B91 3QJ
3. **Manchester:** Think Park, Trafford Park, M17 1FQ

### Contact Numbers
- **Driver Desk:** 0370 419 7000 (Mon-Fri 9-5)
- **New Business:** 0370 600 4499
- **Roadside Assistance:** 24/7 available

### Services
- Personal & Business Contract Hire
- Salary Sacrifice (Ignition scheme)
- Fleet Management
- Flexible Rental
- Electric Vehicle solutions
- Maintenance packages
- Roadside assistance

## YOUR CAPABILITIES
You can:
1. Book appointments (MOT, service, sales, fleet reviews)
2. Capture leads from prospective customers
3. Schedule callbacks
4. Provide roadside assistance info
5. Answer FAQs about leasing, EVs, contracts
6. Transfer calls to specific departments
7. Send SMS appointment confirmations
8. Provide office locations and hours

Always be warm, professional, and solution-focused!
"""

# All 10 tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for MOT, service, inspection, fleet consultation, or sales demo. Use when customer wants to schedule any appointment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer's full name"},
                    "contact_phone": {"type": "string", "description": "Phone number for confirmation"},
                    "contact_email": {"type": "string", "description": "Email address"},
                    "appointment_type": {"type": "string", "enum": ["MOT", "Service", "Inspection", "Fleet Consultation", "Sales Demo"], "description": "Type of appointment"},
                    "preferred_date": {"type": "string", "description": "Preferred date (YYYY-MM-DD format)"},
                    "preferred_time": {"type": "string", "enum": ["Morning (9-12)", "Afternoon (12-3)", "Late Afternoon (3-5)"], "description": "Time slot"},
                    "vehicle_registration": {"type": "string", "description": "Vehicle registration if applicable"},
                    "additional_notes": {"type": "string", "description": "Special requirements"}
                },
                "required": ["customer_name", "contact_phone", "contact_email", "appointment_type", "preferred_date", "preferred_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture lead information from prospective customers interested in fleet leasing or vehicle services.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {"type": "string", "description": "Full name"},
                    "contact_email": {"type": "string", "description": "Email address"},
                    "contact_phone": {"type": "string", "description": "Phone number"},
                    "company_name": {"type": "string", "description": "Company name if business inquiry"},
                    "current_fleet_size": {"type": "integer", "description": "Current number of vehicles"},
                    "vehicle_interests": {"type": "string", "description": "Vehicle types of interest"},
                    "timeline": {"type": "string", "description": "Decision timeline"},
                    "preferred_contact_method": {"type": "string", "enum": ["Phone", "Email", "Either"], "description": "Preferred contact method"}
                },
                "required": ["contact_name", "contact_email", "contact_phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_callback",
            "description": "Schedule a callback request for customers who want to be called back during business hours.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer's name"},
                    "contact_phone": {"type": "string", "description": "Phone number to call back"},
                    "preferred_time": {"type": "string", "description": "Preferred callback time"},
                    "callback_reason": {"type": "string", "description": "Reason for callback"},
                    "is_urgent": {"type": "boolean", "description": "Whether this is urgent"}
                },
                "required": ["customer_name", "contact_phone", "preferred_time", "callback_reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_roadside_assistance",
            "description": "Provide emergency roadside assistance information for breakdowns or vehicle emergencies.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_business_hours",
            "description": "Get current business hours for Arval Driver Desk.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_after_hours",
            "description": "Check if calling outside business hours and provide appropriate guidance.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_faq_answer",
            "description": "Get answers to frequently asked questions about Arval services.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "enum": ["leasing", "fleet", "ev", "mot", "pricing", "contracts", "careers", "general"], "description": "FAQ topic"}
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_call",
            "description": "Transfer the call to a specific department. Use when customer needs to speak with a specialist team.",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {"type": "string", "enum": ["driver_desk", "new_business", "roadside_assistance", "fleet_management", "salary_sacrifice", "end_of_contract"], "description": "Department to transfer to"},
                    "reason": {"type": "string", "description": "Brief reason for transfer"}
                },
                "required": ["department", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_appointment_sms",
            "description": "Send SMS confirmation after booking an appointment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {"type": "string", "description": "Customer phone number"},
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "appointment_type": {"type": "string", "description": "Type of appointment"},
                    "appointment_date": {"type": "string", "description": "Appointment date"},
                    "appointment_time": {"type": "string", "description": "Appointment time"},
                    "location": {"type": "string", "description": "Location or meeting link"}
                },
                "required": ["phone_number", "customer_name", "appointment_type", "appointment_date", "appointment_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_office_locations",
            "description": "Get information about Arval UK office locations and addresses.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


async def deploy():
    """Deploy the updated Arval voice agent to Vapi."""
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("=" * 60)
    print("🚀 DEPLOYING ARVAL VOICE AGENT V2")
    print("=" * 60)
    print()
    
    # Configuration with female voice, end call detection
    config = {
        "name": "Arval Driver Desk - Lily",
        "firstMessage": "Welcome to Arval Driver Desk! My name is Lily, how may I help you?",
        "voice": {
            "provider": "vapi",
            "voiceId": "Lily"
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ],
            "tools": TOOLS,
            "temperature": 0.7
        },
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en-GB"
        },
        # End call settings
        "endCallMessage": "Thank you for calling Arval Driver Desk. Have a wonderful day!",
        "endCallPhrases": [
            "goodbye",
            "bye",
            "that's all",
            "no thanks",
            "nothing else",
            "I'm done",
            "that's everything",
            "have a good day"
        ],
        "silenceTimeoutSeconds": 30,
        "maxDurationSeconds": 1800,  # 30 minutes max
        "backgroundSound": "off",
        "responseDelaySeconds": 0.5,
    }
    
    async with aiohttp.ClientSession() as session:
        # Update assistant
        print("📋 Updating assistant configuration...")
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        
        async with session.patch(url, headers=headers, json=config) as response:
            if response.status == 200:
                data = await response.json()
                print(f"   ✅ Name: {data.get('name')}")
                print(f"   ✅ Voice: Female (Lily)")
                print(f"   ✅ Model: {data.get('model', {}).get('model')}")
                print(f"   ✅ Tools: {len(data.get('model', {}).get('tools', []))}")
                print()
            else:
                error = await response.text()
                print(f"   ❌ Error: {error}")
                return
        
        # Verify phone
        print("📞 Verifying phone connection...")
        phone_url = "https://api.vapi.ai/phone-number"
        async with session.get(phone_url, headers=headers) as response:
            if response.status == 200:
                phones = await response.json()
                for phone in phones:
                    num = phone.get('number', phone.get('phoneNumber', ''))
                    aid = phone.get('assistantId', '')
                    if aid == ASSISTANT_ID:
                        print(f"   ✅ {num} → Arval Driver Desk - Lily")
        
        print()
        print("=" * 60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("=" * 60)
        print()
        print("📞 CALL NOW: +1 (408) 731-2213")
        print()
        print("✨ NEW FEATURES:")
        print("   • Female voice (Lily)")
        print("   • New greeting: 'Welcome to Arval Driver Desk! My name is Lily...'")
        print("   • Automatic call ending detection")
        print("   • 10 tools including call transfer & SMS")
        print("   • Empathetic, professional personality")
        print("   • Complete UK office information")
        print()
        print("🌐 Dashboard: https://dashboard.vapi.ai")
        print()


if __name__ == "__main__":
    asyncio.run(deploy())
