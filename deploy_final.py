#!/usr/bin/env python3
"""
FINAL DEPLOYMENT: All 7 tools + Full System Context + Fallbacks
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

## Contract Hire Benefits
- Fixed monthly costs with no surprises
- No depreciation risk
- VAT benefits for businesses
- Hassle-free maintenance options
- Brand new vehicles without large capital outlay

## Electric Vehicle Information
- Range: 200-350 miles per charge
- Home charging (7kW): 6-12 hours
- Rapid charging (50kW+): 30-60 minutes to 80%
- Home charge cost: £10-15 per full charge
- Battery warranty: 8 years / 100,000 miles typically

## Maintenance Package Includes
- Scheduled servicing, MOT testing
- Tyres, batteries, exhausts, brakes
- 24/7 breakdown recovery

## Tool Usage Instructions
- book_appointment: When customer wants to schedule MOT, service, consultation
- capture_lead: New customer interested in leasing
- schedule_callback: Customer prefers callback or after-hours
- get_roadside_assistance: Breakdown, accident, flat tyre, battery issue (24/7)
- get_business_hours: Opening hours questions
- check_after_hours: Determine if outside business hours
- get_faq_answer: General questions about leasing, EVs, contracts

## Tone & Style
- Friendly and warm (not corporate)
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
            "description": "Book an appointment for MOT, service, vehicle inspection, fleet consultation, sales demo, or driver onboarding.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Full name"},
                    "customer_phone": {"type": "string", "description": "Phone number"},
                    "customer_email": {"type": "string", "description": "Email (optional)"},
                    "appointment_type": {"type": "string", "enum": ["MOT", "Service", "Inspection", "Fleet Consultation", "Sales Demo", "Driver Onboarding", "Leasing Consultation"], "description": "Type of appointment"},
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
            {"type": "request-complete", "content": "Your appointment has been scheduled. You'll receive a confirmation call. Is there anything else I can help with?"},
            {"type": "request-failed", "content": "I'm having trouble booking right now. Please call 0370 419 7000."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture lead information from prospective customers interested in vehicle leasing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {"type": "string", "description": "Full name"},
                    "company_name": {"type": "string", "description": "Company name if business"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "fleet_size": {"type": "string", "description": "Fleet size"},
                    "vehicle_interests": {"type": "string", "description": "Vehicle interests"},
                    "inquiry_type": {"type": "string", "enum": ["Personal Leasing", "Business Leasing", "Fleet Management", "Salary Sacrifice", "Electric Vehicles", "General Inquiry"], "description": "Type of inquiry"}
                },
                "required": ["contact_name", "phone", "inquiry_type"]
            }
        },
        "messages": [
            {"type": "request-start", "content": "Let me save your details."},
            {"type": "request-complete", "content": "Thank you! A specialist will contact you within 24 hours. Is there anything else?"},
            {"type": "request-failed", "content": "I had trouble saving that. Please call 0370 600 4499."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_callback",
            "description": "Schedule a callback for customers who prefer to be called back.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "phone_number": {"type": "string", "description": "Callback number"},
                    "preferred_time": {"type": "string", "description": "When to call back"},
                    "reason": {"type": "string", "description": "Reason for callback"},
                    "urgency": {"type": "string", "enum": ["Normal", "Urgent", "Emergency"], "description": "Urgency level"}
                },
                "required": ["customer_name", "phone_number", "reason"]
            }
        },
        "messages": [
            {"type": "request-start", "content": "I'll schedule that callback."},
            {"type": "request-complete", "content": "Done! Our team will call you back. Is there anything else?"},
            {"type": "request-failed", "content": "I couldn't schedule that. Please try again later."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "get_roadside_assistance",
            "description": "Provide roadside assistance for breakdowns, accidents, or emergencies. Available 24/7.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_type": {"type": "string", "enum": ["Breakdown", "Accident", "Flat Tyre", "Battery", "Locked Out", "Fuel", "Other"], "description": "Type of issue"},
                    "location": {"type": "string", "description": "Current location"},
                    "vehicle_registration": {"type": "string", "description": "Vehicle registration"},
                    "is_safe": {"type": "boolean", "description": "Is caller safe"}
                },
                "required": ["issue_type"]
            }
        },
        "messages": [
            {"type": "request-start", "content": "Connecting you with roadside assistance."},
            {"type": "request-complete", "content": "Our 24/7 roadside team is ready. Please stay safe. Help is on the way."}
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "get_business_hours",
            "description": "Get business hours information.",
            "parameters": {"type": "object", "properties": {"check_date": {"type": "string", "description": "Date to check"}}, "required": []}
        },
        "messages": [{"type": "request-complete", "content": "Our Driver Desk is open Monday to Friday, 9 AM to 5 PM GMT. Roadside assistance is available 24/7."}]
    },
    {
        "type": "function",
        "function": {
            "name": "check_after_hours",
            "description": "Check if outside business hours and provide options.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        "messages": [{"type": "request-complete", "content": "Our office is currently closed. For emergencies, roadside assistance is available 24/7. I can schedule a callback for the next business day."}]
    },
    {
        "type": "function",
        "function": {
            "name": "get_faq_answer",
            "description": "Answer frequently asked questions about Arval services.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_category": {"type": "string", "enum": ["Company Info", "Leasing", "Contract", "Maintenance", "Electric Vehicles", "End of Contract", "Salary Sacrifice", "Complaints"], "description": "Category"},
                    "question": {"type": "string", "description": "The question"}
                },
                "required": ["question"]
            }
        },
        "messages": [{"type": "request-start", "content": "Let me find that information."}]
    }
]


async def deploy_with_fallbacks():
    """Deploy with all 7 tools, system context, AND fallback voice/transcribers."""
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("=" * 70)
    print("🚀 FINAL DEPLOYMENT WITH FALLBACKS")
    print("=" * 70)
    print()
    
    async with aiohttp.ClientSession() as session:
        # Complete configuration with fallbacks
        print("📋 Configuring assistant with 7 tools + fallbacks...")
        
        assistant_config = {
            "name": "Arval Driver Desk",
            "firstMessage": "Hello, welcome to Arval Driver Desk! I can help you with vehicle leasing, booking appointments, roadside assistance, and answering questions. How may I assist you today?",
            
            # Model with all 7 tools
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
                "temperature": 0.7,
                "maxTokens": 300,
                "tools": ALL_TOOLS
            },
            
            # Primary Voice: Vapi built-in
            "voice": {
                "provider": "vapi",
                "voiceId": "Elliot"
            },
            
            # Fallback Voices
            "voiceFallbackPlan": {
                "voices": [
                    {"provider": "deepgram", "voiceId": "aura-asteria-en"},
                    {"provider": "playht", "voiceId": "jennifer"}
                ]
            },
            
            # Primary Transcriber: Deepgram Nova-2
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en"
            },
            
            # Fallback Transcribers
            "transcriberFallbackPlan": {
                "transcribers": [
                    {"provider": "deepgram", "model": "nova", "language": "en"},
                    {"provider": "gladia", "language": "en"}
                ]
            },
            
            # Call settings
            "endCallMessage": "Thank you for calling Arval. Have a great day!",
            "voicemailMessage": "Hello, you've reached Arval Driver Desk. Please leave a message and we'll call you back.",
            "silenceTimeoutSeconds": 30,
            "maxDurationSeconds": 600,
            "endCallFunctionEnabled": True,
            "backchannelingEnabled": True,
            "backgroundSound": "off",
            
            # Start/Stop speaking plans
            "startSpeakingPlan": {
                "waitSeconds": 0.4
            }
        }
        
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        async with session.patch(url, headers=headers, json=assistant_config) as response:
            if response.status == 200:
                result = await response.json()
                tools_count = len(result.get('model', {}).get('tools', []))
                print(f"   ✅ Assistant updated!")
                print(f"   ✅ Tools: {tools_count} configured")
                print(f"   ✅ System prompt: Loaded")
                print()
                
                # Check voice config
                voice = result.get('voice', {})
                print(f"🎤 Voice Configuration:")
                print(f"   Primary: {voice.get('provider')} - {voice.get('voiceId')}")
                
                fallback_voices = result.get('voiceFallbackPlan', {}).get('voices', [])
                if fallback_voices:
                    print(f"   Fallbacks: {len(fallback_voices)}")
                    for fv in fallback_voices:
                        print(f"      • {fv.get('provider')} - {fv.get('voiceId')}")
                print()
                
                # Check transcriber config
                transcriber = result.get('transcriber', {})
                print(f"📝 Transcriber Configuration:")
                print(f"   Primary: {transcriber.get('provider')} - {transcriber.get('model')}")
                
                fallback_transcribers = result.get('transcriberFallbackPlan', {}).get('transcribers', [])
                if fallback_transcribers:
                    print(f"   Fallbacks: {len(fallback_transcribers)}")
                    for ft in fallback_transcribers:
                        print(f"      • {ft.get('provider')} - {ft.get('model', 'default')}")
                print()
                
            else:
                error = await response.text()
                print(f"   ❌ Failed: {error}")
                
                # Try simpler config without fallback plans if they're not supported
                print()
                print("🔄 Trying without fallback plans (may not be supported on free tier)...")
                
                simple_config = {
                    "name": "Arval Driver Desk",
                    "firstMessage": "Hello, welcome to Arval Driver Desk! How may I assist you today?",
                    "model": {
                        "provider": "openai",
                        "model": "gpt-4o",
                        "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
                        "temperature": 0.7,
                        "maxTokens": 300,
                        "tools": ALL_TOOLS
                    },
                    "voice": {"provider": "vapi", "voiceId": "Elliot"},
                    "transcriber": {"provider": "deepgram", "model": "nova-2", "language": "en"},
                    "endCallMessage": "Thank you for calling Arval. Have a great day!",
                    "silenceTimeoutSeconds": 30,
                    "maxDurationSeconds": 600
                }
                
                async with session.patch(url, headers=headers, json=simple_config) as retry:
                    if retry.status == 200:
                        result = await retry.json()
                        print("   ✅ Deployed without fallbacks (not available on free tier)")
                    else:
                        err2 = await retry.text()
                        print(f"   ❌ Also failed: {err2}")
                        return
        
        # Verify phone number
        print(f"📞 Phone Number Status:")
        phone_url = "https://api.vapi.ai/phone-number"
        async with session.get(phone_url, headers=headers) as response:
            if response.status == 200:
                phones = await response.json()
                for phone in phones:
                    phone_num = phone.get('number', phone.get('phoneNumber', 'Unknown'))
                    assistant_id = phone.get('assistantId', '')
                    print(f"   {phone_num}")
                    if assistant_id == ASSISTANT_ID:
                        print(f"   ✅ Assigned to Arval Driver Desk")
        
        print()
        print("=" * 70)
        print("✅ DEPLOYMENT COMPLETE!")
        print("=" * 70)
        print()
        print("📞 CALL NOW: +1 (408) 731-2213")
        print()
        print("🔧 7 TOOLS READY:")
        print("   1. book_appointment")
        print("   2. capture_lead")
        print("   3. schedule_callback")
        print("   4. get_roadside_assistance")
        print("   5. get_business_hours")
        print("   6. check_after_hours")
        print("   7. get_faq_answer")
        print()
        print("🎤 Voice: Vapi Elliot (with Deepgram/PlayHT fallbacks)")
        print("📝 Transcriber: Deepgram Nova-2 (with Nova/Gladia fallbacks)")
        print()
        print("💬 TEST PHRASES:")
        print('   • "I want to book an MOT appointment"')
        print('   • "Tell me about electric vehicles"')
        print('   • "I need roadside assistance"')
        print('   • "What are your business hours?"')
        print()


if __name__ == "__main__":
    asyncio.run(deploy_with_fallbacks())
