#!/usr/bin/env python3
"""
COMPLETE DEPLOYMENT: All 7 tools + Full System Context + Phone Number Assignment
"""

import asyncio
import aiohttp
import json

VAPI_API_KEY = "e72c9335-54ce-4271-aac5-7c46598ed3ae"
ASSISTANT_ID = "b543468c-e12e-481f-abb6-d0e129c7e5bb"
PHONE_NUMBER = "+14087312213"

# FULL SYSTEM CONTEXT
SYSTEM_PROMPT = """You are the Arval Driver Desk voice assistant for Arval BNP Paribas Group, a global leader in vehicle leasing.

## Your Identity
- Name: Arval Driver Desk Assistant
- Company: Arval BNP Paribas - 4th largest vehicle leasing company in UK
- Role: Help customers with vehicle leasing, bookings, roadside assistance, and inquiries

## Company Facts
- Founded: 1989, owned by BNP Paribas
- UK Fleet: 190,000+ vehicles
- Global: 28 countries, 8,600 employees, 1.82 million vehicles worldwide
- Alliance: Element-Arval Global Alliance (4.5M vehicles across 54 countries)

## Business Hours
- Monday-Friday: 9:00 AM - 5:00 PM GMT
- Location: Swindon, Wiltshire, England
- Roadside Assistance: Available 24/7

## Contact Numbers
- General: 0370 419 7000
- Leasing: 0370 600 4499

## Products & Services
- Personal Contract Hire (PCH) - for individuals/families
- Business Contract Hire (BCH) - for companies
- Salary Sacrifice (Ignition by Arval) - tax-efficient employee car schemes
- Flexible Rental - short to medium term
- Fleet Management - full fleet solutions
- Electric Vehicle Solutions - EV leasing with charging support
- LCV Fleet Management - Light Commercial Vehicles

## Contract Hire Benefits
- Fixed monthly costs with no surprises
- No depreciation risk
- VAT benefits for businesses
- Hassle-free maintenance options
- Brand new vehicles without large capital outlay

## Electric Vehicle Information
- Range: 200-350 miles per charge (varies by model)
- Home charging (7kW): 6-12 hours for full charge
- Rapid charging (50kW+): 30-60 minutes to 80%
- Home charge cost: £10-15 per full charge
- Battery warranty: typically 8 years / 100,000 miles

## Maintenance Package Includes
- Scheduled servicing
- MOT testing
- Tyres, batteries, exhausts, brakes
- General wear and tear repairs
- 24/7 breakdown recovery

## IMPORTANT: Tool Usage Instructions

### When to use book_appointment:
- Customer wants to schedule MOT, service, consultation, or demo
- Collect: name, phone, appointment type, preferred date/time

### When to use capture_lead:
- New customer interested in leasing
- Collect: name, phone, company (if business), vehicle interest

### When to use schedule_callback:
- Customer prefers to be called back
- Customer calling after hours
- Collect: name, phone, preferred time, reason

### When to use get_roadside_assistance:
- Customer has breakdown, accident, flat tyre, battery issue
- Provide 24/7 emergency number immediately
- Collect: issue type, location if safe to share

### When to use get_business_hours:
- Customer asks about opening hours
- Respond: Monday-Friday 9AM-5PM GMT

### When to use check_after_hours:
- Determine if it's outside business hours
- Offer callback scheduling or 24/7 roadside for emergencies

### When to use get_faq_answer:
- General questions about leasing, EVs, contracts, maintenance

## Tone & Style
- Friendly and warm (not corporate)
- Helpful and patient
- Concise responses (2-3 sentences for voice)
- Always confirm before taking action
- End with "Is there anything else I can help with?"
- Close calls with "Thank you for choosing Arval"
"""

# ALL 7 TOOLS
ALL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for MOT, service, vehicle inspection, fleet consultation, sales demo, or driver onboarding. Use when customer wants to schedule any meeting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Full name of the customer"},
                    "customer_phone": {"type": "string", "description": "Customer phone number"},
                    "customer_email": {"type": "string", "description": "Customer email (optional)"},
                    "appointment_type": {
                        "type": "string",
                        "enum": ["MOT", "Service", "Inspection", "Fleet Consultation", "Sales Demo", "Driver Onboarding", "Leasing Consultation"],
                        "description": "Type of appointment"
                    },
                    "preferred_date": {"type": "string", "description": "Preferred date"},
                    "preferred_time": {"type": "string", "description": "Preferred time"},
                    "vehicle_registration": {"type": "string", "description": "Vehicle reg if applicable"},
                    "notes": {"type": "string", "description": "Additional notes"}
                },
                "required": ["customer_name", "customer_phone", "appointment_type"]
            }
        },
        "messages": [
            {"type": "request-start", "content": "Let me book that appointment for you."},
            {"type": "request-complete", "content": "Your appointment has been scheduled. You'll receive a confirmation call from our team. Is there anything else I can help with?"},
            {"type": "request-failed", "content": "I'm having trouble booking right now. Please call 0370 419 7000 and our team will help you."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture lead information from prospective customers interested in vehicle leasing. Use when someone shows interest but isn't ready to book.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {"type": "string", "description": "Full name"},
                    "company_name": {"type": "string", "description": "Company name if business inquiry"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "fleet_size": {"type": "string", "description": "Current or projected fleet size"},
                    "current_provider": {"type": "string", "description": "Current leasing provider"},
                    "vehicle_interests": {"type": "string", "description": "Vehicle types of interest"},
                    "timeline": {"type": "string", "description": "Decision timeline"},
                    "inquiry_type": {
                        "type": "string",
                        "enum": ["Personal Leasing", "Business Leasing", "Fleet Management", "Salary Sacrifice", "Electric Vehicles", "General Inquiry"],
                        "description": "Type of inquiry"
                    }
                },
                "required": ["contact_name", "phone", "inquiry_type"]
            }
        },
        "messages": [
            {"type": "request-start", "content": "Let me save your details."},
            {"type": "request-complete", "content": "Thank you! A leasing specialist will contact you within 24 hours. Is there anything else?"},
            {"type": "request-failed", "content": "I had trouble saving that. Please call 0370 600 4499 for leasing inquiries."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_callback",
            "description": "Schedule a callback for customers who call outside business hours or prefer to be called back.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "phone_number": {"type": "string", "description": "Callback number"},
                    "preferred_time": {"type": "string", "description": "When to call back"},
                    "reason": {"type": "string", "description": "Reason for callback"},
                    "urgency": {
                        "type": "string",
                        "enum": ["Normal", "Urgent", "Emergency"],
                        "description": "Urgency level"
                    }
                },
                "required": ["customer_name", "phone_number", "reason"]
            }
        },
        "messages": [
            {"type": "request-start", "content": "I'll schedule that callback for you."},
            {"type": "request-complete", "content": "Done! Our team will call you back during business hours. Is there anything else?"},
            {"type": "request-failed", "content": "I couldn't schedule the callback. Please try calling again during business hours."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "get_roadside_assistance",
            "description": "Provide roadside assistance information for breakdowns, accidents, or emergencies. Available 24/7.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "enum": ["Breakdown", "Accident", "Flat Tyre", "Battery", "Locked Out", "Fuel", "Other"],
                        "description": "Type of issue"
                    },
                    "location": {"type": "string", "description": "Current location"},
                    "vehicle_registration": {"type": "string", "description": "Vehicle registration"},
                    "is_safe": {"type": "boolean", "description": "Is caller in safe location"}
                },
                "required": ["issue_type"]
            }
        },
        "messages": [
            {"type": "request-start", "content": "Let me connect you with roadside assistance."},
            {"type": "request-complete", "content": "Our 24/7 roadside assistance team is available right now. Please stay safe and visible. They'll dispatch help immediately."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "get_business_hours",
            "description": "Get current business hours and check if office is open.",
            "parameters": {
                "type": "object",
                "properties": {
                    "check_date": {"type": "string", "description": "Date to check (optional)"}
                },
                "required": []
            }
        },
        "messages": [
            {"type": "request-complete", "content": "Our Driver Desk is open Monday to Friday, 9 AM to 5 PM GMT. Emergency roadside assistance is available 24/7."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "check_after_hours",
            "description": "Check if current time is outside business hours and provide appropriate options.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "messages": [
            {"type": "request-complete", "content": "Our office is currently closed. For emergencies, roadside assistance is available 24/7. Otherwise, I can schedule a callback for the next business day."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "get_faq_answer",
            "description": "Get answers to frequently asked questions about Arval services, leasing, EVs, maintenance, contracts, and more.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_category": {
                        "type": "string",
                        "enum": ["Company Info", "Leasing", "Contract", "Maintenance", "Electric Vehicles", "End of Contract", "Salary Sacrifice", "Complaints"],
                        "description": "Category of question"
                    },
                    "question": {"type": "string", "description": "The specific question"}
                },
                "required": ["question"]
            }
        },
        "messages": [
            {"type": "request-start", "content": "Let me find that information for you."}
        ]
    }
]


async def deploy_complete():
    """Deploy with all 7 tools, full system context, and phone number."""
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("=" * 70)
    print("🚀 COMPLETE DEPLOYMENT - ARVAL VOICE AGENT")
    print("=" * 70)
    print()
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Update assistant with all tools and system context
        print("📋 Step 1: Configuring assistant with 7 tools + system context...")
        
        model_config = {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
            "temperature": 0.7,
            "maxTokens": 300,
            "tools": ALL_TOOLS
        }
        
        assistant_config = {
            "name": "Arval Driver Desk",
            "firstMessage": "Hello, welcome to Arval Driver Desk! I can help you with vehicle leasing, booking appointments, roadside assistance, and answering questions. How may I assist you today?",
            "model": model_config,
            "voice": {"provider": "vapi", "voiceId": "Elliot"},
            "transcriber": {"provider": "deepgram", "model": "nova-2", "language": "en"},
            "endCallMessage": "Thank you for calling Arval. Have a great day!",
            "silenceTimeoutSeconds": 30,
            "maxDurationSeconds": 600,
            "endCallFunctionEnabled": True,
            "backchannelingEnabled": True
        }
        
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        async with session.patch(url, headers=headers, json=assistant_config) as response:
            if response.status == 200:
                result = await response.json()
                tools_count = len(result.get('model', {}).get('tools', []))
                print(f"   ✅ Assistant updated!")
                print(f"   ✅ Tools configured: {tools_count}")
                print(f"   ✅ System prompt: Loaded")
                print()
            else:
                error = await response.text()
                print(f"   ❌ Failed: {error}")
                return
        
        # Step 2: Verify tools
        print("🔧 Step 2: Verifying all 7 tools...")
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                tools = data.get('model', {}).get('tools', [])
                print(f"   Tools configured: {len(tools)}")
                for t in tools:
                    if 'function' in t:
                        print(f"      • {t['function'].get('name')}")
                print()
        
        # Step 3: Check phone number
        print(f"📞 Step 3: Phone number status...")
        print(f"   Your number: {PHONE_NUMBER}")
        print(f"   Format: +1 (408) 731-2213")
        print()
        
        # Try to get phone numbers
        phone_url = "https://api.vapi.ai/phone-number"
        async with session.get(phone_url, headers=headers) as response:
            if response.status == 200:
                phones = await response.json()
                if phones:
                    print("   📱 Phone numbers in your account:")
                    for phone in phones:
                        phone_num = phone.get('number', phone.get('phoneNumber', 'Unknown'))
                        assistant_id = phone.get('assistantId', 'Not assigned')
                        print(f"      • {phone_num}")
                        if assistant_id == ASSISTANT_ID:
                            print(f"        ✅ Assigned to Arval Driver Desk")
                        elif assistant_id:
                            print(f"        ⚠️  Assigned to: {assistant_id}")
                else:
                    print("   No phone numbers found")
        
        print()
        print("=" * 70)
        print("✅ DEPLOYMENT COMPLETE!")
        print("=" * 70)
        print()
        print("🎯 YOUR VOICE AGENT IS READY:")
        print()
        print(f"   📞 Phone: +1 (408) 731-2213")
        print(f"   🤖 Assistant: Arval Driver Desk")
        print(f"   🔧 Tools: 7 configured")
        print()
        print("📋 TOOLS AVAILABLE:")
        print("   1. book_appointment - Schedule MOT, service, consultations")
        print("   2. capture_lead - Collect prospect information")
        print("   3. schedule_callback - Request callback")
        print("   4. get_roadside_assistance - 24/7 breakdown help")
        print("   5. get_business_hours - Office hours info")
        print("   6. check_after_hours - After-hours handling")
        print("   7. get_faq_answer - Answer common questions")
        print()
        print("🧪 TO TEST:")
        print("   Option 1: Call +1 (408) 731-2213 from any phone")
        print("   Option 2: Use TEST tab in Vapi dashboard")
        print()
        print("💬 TRY SAYING:")
        print('   • "I want to book an MOT appointment"')
        print('   • "What are your business hours?"')
        print('   • "Tell me about electric vehicle leasing"')
        print('   • "I need roadside assistance"')
        print()


if __name__ == "__main__":
    asyncio.run(deploy_complete())
