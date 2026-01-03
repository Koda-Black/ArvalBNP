#!/usr/bin/env python3
"""
COMPLETE Vapi Assistant Setup
This script properly configures everything: system prompt, tools, and all settings.
"""

import asyncio
import aiohttp
import json

VAPI_API_KEY = "e72c9335-54ce-4271-aac5-7c46598ed3ae"
ASSISTANT_ID = "b543468c-e12e-481f-abb6-d0e129c7e5bb"

# Full system prompt with all knowledge
SYSTEM_PROMPT = """You are the Arval Driver Desk voice assistant for Arval BNP Paribas Group.

## Your Identity
- Name: Arval Driver Desk Assistant
- Company: Arval BNP Paribas - 4th largest vehicle leasing company in UK
- Role: Help customers with vehicle leasing, bookings, and inquiries

## Company Facts (USE THESE IN RESPONSES)
- Founded: 1989
- Parent: BNP Paribas
- UK Fleet: 190,000+ vehicles
- Global: 28 countries, 8,600 employees, 1.82 million vehicles
- Alliance: Element-Arval Global Alliance (4.5M vehicles, 54 countries)

## Business Hours
- Monday-Friday: 9:00 AM - 5:00 PM GMT
- Location: Swindon, Wiltshire, England
- Roadside Assistance: 24/7

## Contact Numbers
- General: 0370 419 7000
- Leasing: 0370 600 4499

## Products & Services
- Personal Contract Hire (PCH) - for individuals
- Business Contract Hire (BCH) - for companies
- Salary Sacrifice (Ignition by Arval) - tax-efficient employee schemes
- Flexible Rental - short to medium term
- Fleet Management - full fleet solutions
- Electric Vehicles - EV leasing and charging solutions

## Key Information

### Contract Hire Benefits
- Fixed monthly costs
- No depreciation risk
- VAT benefits for businesses
- Hassle-free maintenance options
- New vehicles without large capital outlay

### EV Information
- Range: 200-350 miles per charge
- Home charging (7kW): 6-12 hours
- Rapid charging (50kW+): 30-60 minutes to 80%
- Home charge cost: £10-15 per full charge
- Battery warranty: 8 years / 100,000 miles typically

### Maintenance
- Servicing, MOT, tyres, batteries, brakes included in maintenance package
- 24/7 breakdown recovery available
- First MOT due after 3 years for new vehicles

## CRITICAL INSTRUCTIONS

### When Customer Wants to Book a Meeting/Appointment:
1. Use the book_appointment function
2. Collect: name, phone, preferred date/time, appointment type
3. Confirm the booking details back to them

### When Customer Asks About Pricing:
- For specific quotes, offer to book a consultation
- Or direct them to call 0370 600 4499
- Explain that pricing depends on vehicle, term, mileage, and services

### Your Tone
- Friendly and warm (not corporate)
- Helpful and patient
- Always confirm understanding before taking action
- End with "Is there anything else I can help you with?"

### Response Style
- Keep responses concise for voice (2-3 sentences max)
- Don't read out long lists - summarize and offer to elaborate
- Use natural conversational language
- Confirm important details before booking
"""

# Define the tools/functions for the assistant
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment or meeting for the customer. Use this when customer wants to schedule a meeting, consultation, MOT, service, or any appointment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Full name of the customer"
                    },
                    "customer_phone": {
                        "type": "string",
                        "description": "Customer phone number"
                    },
                    "customer_email": {
                        "type": "string",
                        "description": "Customer email address (optional)"
                    },
                    "appointment_type": {
                        "type": "string",
                        "enum": ["Leasing Consultation", "MOT", "Service", "Fleet Consultation", "Sales Demo", "General Inquiry"],
                        "description": "Type of appointment"
                    },
                    "preferred_date": {
                        "type": "string",
                        "description": "Preferred date (e.g., 'tomorrow', 'next Monday', '15th January')"
                    },
                    "preferred_time": {
                        "type": "string",
                        "description": "Preferred time (e.g., 'morning', '2pm', 'afternoon')"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Any additional notes or vehicle interests"
                    }
                },
                "required": ["customer_name", "customer_phone", "appointment_type"]
            }
        },
        "async": False,
        "messages": [
            {
                "type": "request-start",
                "content": "Let me book that appointment for you now."
            },
            {
                "type": "request-complete", 
                "content": "I've scheduled your appointment. You'll receive a confirmation call from our team to finalize the details. Is there anything else I can help you with?"
            },
            {
                "type": "request-failed",
                "content": "I apologize, I'm having trouble booking right now. Please call us directly at 0370 419 7000 and our team will be happy to schedule your appointment."
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture contact details for customers interested in leasing. Use when customer shows interest but isn't ready to book.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {
                        "type": "string",
                        "description": "Customer's full name"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Phone number"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email address"
                    },
                    "interest": {
                        "type": "string",
                        "description": "What they're interested in (vehicle type, service, etc.)"
                    },
                    "company_name": {
                        "type": "string",
                        "description": "Company name if business inquiry"
                    },
                    "fleet_size": {
                        "type": "string",
                        "description": "Current or expected fleet size"
                    }
                },
                "required": ["contact_name", "phone", "interest"]
            }
        },
        "async": False,
        "messages": [
            {
                "type": "request-start",
                "content": "Let me save your details."
            },
            {
                "type": "request-complete",
                "content": "Thank you! I've noted your details. One of our specialists will be in touch within 24 hours. Is there anything else I can help with?"
            }
        ]
    },
    {
        "type": "function", 
        "function": {
            "name": "schedule_callback",
            "description": "Schedule a callback for the customer. Use when customer prefers to be called back.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Customer's name"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Number to call back"
                    },
                    "preferred_time": {
                        "type": "string",
                        "description": "When they'd like to be called"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for callback"
                    }
                },
                "required": ["customer_name", "phone_number", "reason"]
            }
        },
        "async": False,
        "messages": [
            {
                "type": "request-start",
                "content": "I'll schedule that callback for you."
            },
            {
                "type": "request-complete",
                "content": "Perfect! Our team will call you back. Is there anything else I can help with?"
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "get_roadside_assistance",
            "description": "Provide roadside assistance information for breakdowns or emergencies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "enum": ["Breakdown", "Accident", "Flat Tyre", "Battery", "Locked Out", "Other"],
                        "description": "Type of issue"
                    },
                    "location": {
                        "type": "string",
                        "description": "Current location"
                    },
                    "vehicle_reg": {
                        "type": "string",
                        "description": "Vehicle registration"
                    }
                },
                "required": ["issue_type"]
            }
        },
        "async": False,
        "messages": [
            {
                "type": "request-complete",
                "content": "For immediate roadside assistance, our 24/7 team is ready to help. Please stay safe and they'll dispatch help to your location right away."
            }
        ]
    }
]


async def complete_setup():
    """Completely reconfigure the Vapi assistant with all settings."""
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Complete configuration
    config = {
        "name": "Arval Driver Desk",
        "firstMessage": "Hello, welcome to Arval Driver Desk! I can help you with vehicle leasing, booking appointments, and answering any questions. How may I assist you today?",
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ],
            "temperature": 0.7,
            "maxTokens": 250
        },
        "voice": {
            "provider": "vapi",
            "voiceId": "Elliot"
        },
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en"
        },
        "tools": TOOLS,
        "silenceTimeoutSeconds": 30,
        "maxDurationSeconds": 600,
        "endCallMessage": "Thank you for calling Arval. Have a great day!",
        "voicemailMessage": "Hello, you've reached Arval Driver Desk. Please leave a message and we'll call you back.",
        "endCallFunctionEnabled": True,
        "backgroundSound": "off",
        "backchannelingEnabled": True,
        "startSpeakingPlan": {
            "waitSeconds": 0.4
        }
    }
    
    print("=" * 70)
    print("🔧 COMPLETE VAPI ASSISTANT SETUP")
    print("=" * 70)
    print()
    print("Configuring:")
    print("  ✓ System prompt with full Arval knowledge")
    print("  ✓ 4 tools: book_appointment, capture_lead, schedule_callback, roadside_assistance")
    print("  ✓ Voice: Vapi Elliot")
    print("  ✓ Transcriber: Deepgram Nova-2")
    print("  ✓ Model: GPT-4o")
    print()
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        
        async with session.patch(url, headers=headers, json=config) as response:
            response_text = await response.text()
            
            if response.status == 200:
                result = json.loads(response_text)
                print("✅ SUCCESS! Assistant fully configured!")
                print()
                print("📋 Verified Configuration:")
                print(f"   • Name: {result.get('name')}")
                print(f"   • Model: {result.get('model', {}).get('model')}")
                print(f"   • Voice: {result.get('voice', {}).get('voiceId')}")
                print(f"   • Tools: {len(result.get('tools', []))} configured")
                print(f"   • First Message: {result.get('firstMessage', '')[:50]}...")
                print()
                
                # Verify tools
                tools = result.get('tools', [])
                if tools:
                    print("🔧 Tools Configured:")
                    for tool in tools:
                        if 'function' in tool:
                            print(f"   • {tool['function'].get('name')}")
                
                print()
                print("=" * 70)
                print("🎤 NOW TEST YOUR ASSISTANT!")
                print("=" * 70)
                print()
                print("1. Go to: https://vapi.ai/dashboard")
                print("2. Click 'Arval Driver Desk'")
                print("3. Click 'TEST' tab")
                print("4. Say: 'I'd like to book a meeting with your leasing team'")
                print()
                print("The assistant should now:")
                print("   ✓ Ask for your name and phone number")
                print("   ✓ Confirm the appointment type")
                print("   ✓ Book the meeting using the tool")
                print()
                return True
            else:
                print(f"❌ Failed: {response.status}")
                print(f"   Response: {response_text}")
                
                # Try without tools first to see if that's the issue
                print()
                print("🔄 Trying without tools first...")
                
                simple_config = {
                    "name": "Arval Driver Desk",
                    "firstMessage": "Hello, welcome to Arval Driver Desk! How may I assist you today?",
                    "model": {
                        "provider": "openai", 
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": SYSTEM_PROMPT
                            }
                        ],
                        "temperature": 0.7
                    },
                    "voice": {
                        "provider": "vapi",
                        "voiceId": "Elliot"
                    },
                    "transcriber": {
                        "provider": "deepgram",
                        "model": "nova-2",
                        "language": "en"
                    }
                }
                
                async with session.patch(url, headers=headers, json=simple_config) as retry:
                    if retry.status == 200:
                        print("✅ Basic config applied (without tools)")
                        print()
                        print("The assistant will now work but without booking capability.")
                        print("It will direct users to call 0370 419 7000 for appointments.")
                        return True
                    else:
                        error2 = await retry.text()
                        print(f"❌ Also failed: {error2}")
                        return False


async def main():
    await complete_setup()


if __name__ == "__main__":
    asyncio.run(main())
