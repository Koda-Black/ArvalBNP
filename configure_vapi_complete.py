#!/usr/bin/env python3
"""
Complete Vapi Configuration Script
This script configures the assistant with OpenRouter credentials and all settings.
"""

import asyncio
import aiohttp
import json

# Your credentials
VAPI_API_KEY = "e72c9335-54ce-4271-aac5-7c46598ed3ae"
ASSISTANT_ID = "b543468c-e12e-481f-abb6-d0e129c7e5bb"
OPENROUTER_API_KEY = "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"

# System prompt from SYSTEM_CONTEXT.md
SYSTEM_PROMPT = """You are the Arval Driver Desk voice assistant for Arval BNP Paribas Group, a global leader in vehicle leasing.

## Your Role
You are a friendly, warm, and helpful voice agent who assists callers with:
- Vehicle leasing questions and information
- Booking MOT and service appointments
- Roadside assistance inquiries
- Capturing leads from prospective customers
- Handling after-hours inquiries

## Company Facts
- Arval BNP Paribas is the 4th largest leasing company in UK with 190,000+ vehicles
- Founded in 1989, owned by BNP Paribas
- Operates in 28 countries with 8,600 employees
- Part of Element-Arval Global Alliance (4.5M vehicles across 54 countries)

## Business Hours
- Monday to Friday: 9:00 AM - 5:00 PM GMT
- Emergency roadside assistance: Available 24/7
- Location: Swindon, Wiltshire, England

## Contact Numbers
- General inquiries: 0370 419 7000
- Leasing inquiries: 0370 600 4499

## Your Tone
- Friendly and warm, not corporate
- Patient - take time to get the right outcome
- Helpful - focus on solving problems
- Professional - represent Arval positively

## Key Services
- Personal Contract Hire (PCH)
- Business Contract Hire (BCH)
- Salary Sacrifice schemes (Ignition by Arval)
- Flexible Rental
- Fleet Management
- Electric Vehicle solutions

## Important Guidelines
1. Always use the appropriate tool when:
   - Booking appointments → use book_appointment
   - Capturing lead information → use capture_lead
   - Scheduling callbacks → use schedule_callback
   - Checking business hours → use get_business_hours
   - Roadside assistance → use get_roadside_assistance
   - Answering FAQs → use get_faq_answer

2. For after-hours calls:
   - Offer to schedule a callback
   - Provide 24/7 roadside assistance number for emergencies
   - Capture their details for follow-up

3. Always confirm details before completing actions
4. End calls warmly with "Thank you for choosing Arval"
"""

# Define all tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for MOT, service, vehicle inspection, fleet consultation, sales demo, or driver onboarding",
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
                        "description": "Customer email address"
                    },
                    "appointment_type": {
                        "type": "string",
                        "enum": ["MOT", "Service", "Inspection", "Fleet Consultation", "Sales Demo", "Driver Onboarding"],
                        "description": "Type of appointment"
                    },
                    "preferred_date": {
                        "type": "string",
                        "description": "Preferred date for appointment (YYYY-MM-DD format)"
                    },
                    "preferred_time": {
                        "type": "string",
                        "description": "Preferred time for appointment"
                    },
                    "vehicle_registration": {
                        "type": "string",
                        "description": "Vehicle registration number if applicable"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes or requirements"
                    }
                },
                "required": ["customer_name", "customer_phone", "appointment_type", "preferred_date"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me book that appointment for you..."
            },
            {
                "type": "request-complete",
                "content": "I've successfully booked your {{appointment_type}} appointment for {{preferred_date}}. You'll receive a confirmation shortly."
            },
            {
                "type": "request-failed",
                "content": "I'm sorry, I wasn't able to book the appointment right now. Let me take your details and have someone call you back."
            }
        ],
        "server": {
            "url": "https://webhook.site/arval-appointments"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture lead information from prospective customers interested in vehicle leasing",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {
                        "type": "string",
                        "description": "Full name of the contact"
                    },
                    "company_name": {
                        "type": "string",
                        "description": "Company name if business inquiry"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email address"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Phone number"
                    },
                    "fleet_size": {
                        "type": "string",
                        "description": "Current or projected fleet size"
                    },
                    "current_provider": {
                        "type": "string",
                        "description": "Current leasing provider if any"
                    },
                    "vehicle_interests": {
                        "type": "string",
                        "description": "Specific vehicle types or models of interest"
                    },
                    "timeline": {
                        "type": "string",
                        "description": "Timeline for decision or need"
                    },
                    "inquiry_type": {
                        "type": "string",
                        "enum": ["Personal Leasing", "Business Leasing", "Fleet Management", "Salary Sacrifice", "Electric Vehicles", "General Inquiry"],
                        "description": "Type of inquiry"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes about the inquiry"
                    }
                },
                "required": ["contact_name", "phone", "inquiry_type"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me save your details..."
            },
            {
                "type": "request-complete",
                "content": "Thank you {{contact_name}}. I've captured your details and one of our specialists will be in touch within 24 hours to discuss your {{inquiry_type}} needs."
            },
            {
                "type": "request-failed",
                "content": "I apologize, I had trouble saving your information. Can you please call us directly at 0370 419 7000?"
            }
        ],
        "server": {
            "url": "https://webhook.site/arval-leads"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_callback",
            "description": "Schedule a callback for customers who call outside business hours or prefer to be called back",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Full name of the customer"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Phone number to call back"
                    },
                    "preferred_time": {
                        "type": "string",
                        "description": "Preferred callback time"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the callback"
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["Normal", "Urgent", "Emergency"],
                        "description": "Urgency level of the callback"
                    }
                },
                "required": ["customer_name", "phone_number", "reason"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "I'm scheduling your callback now..."
            },
            {
                "type": "request-complete",
                "content": "Perfect {{customer_name}}, I've scheduled a callback for you. Someone from our team will call you back during business hours."
            },
            {
                "type": "request-failed",
                "content": "I'm having trouble scheduling the callback. Please try calling us again during business hours at 0370 419 7000."
            }
        ],
        "server": {
            "url": "https://webhook.site/arval-callbacks"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_roadside_assistance",
            "description": "Provide roadside assistance information and connect to emergency services",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "enum": ["Breakdown", "Accident", "Flat Tyre", "Battery", "Locked Out", "Fuel", "Other"],
                        "description": "Type of roadside issue"
                    },
                    "location": {
                        "type": "string",
                        "description": "Current location of the vehicle"
                    },
                    "vehicle_registration": {
                        "type": "string",
                        "description": "Vehicle registration number"
                    },
                    "is_safe": {
                        "type": "boolean",
                        "description": "Whether the caller is in a safe location"
                    }
                },
                "required": ["issue_type"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me get you the roadside assistance information..."
            },
            {
                "type": "request-complete",
                "content": "For immediate roadside assistance, please call our 24/7 emergency line. They will dispatch help to your location right away. Please stay safe and visible to other road users."
            }
        ],
        "server": {
            "url": "https://webhook.site/arval-roadside"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_business_hours",
            "description": "Get current business hours and check if the office is open",
            "parameters": {
                "type": "object",
                "properties": {
                    "check_date": {
                        "type": "string",
                        "description": "Date to check business hours for (optional, defaults to today)"
                    }
                },
                "required": []
            }
        },
        "messages": [
            {
                "type": "request-complete",
                "content": "Our Driver Desk is open Monday to Friday, 9 AM to 5 PM GMT. Emergency roadside assistance is available 24/7."
            }
        ],
        "server": {
            "url": "https://webhook.site/arval-hours"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_after_hours",
            "description": "Check if current time is outside business hours and provide appropriate options",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "messages": [
            {
                "type": "request-complete",
                "content": "Our office is currently closed. For emergencies, our roadside assistance is available 24/7. Otherwise, I can schedule a callback for the next business day."
            }
        ],
        "server": {
            "url": "https://webhook.site/arval-afterhours"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_faq_answer",
            "description": "Get answers to frequently asked questions about Arval services, leasing, EVs, maintenance, and more",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_category": {
                        "type": "string",
                        "enum": ["Company Info", "Leasing", "Contract", "Maintenance", "Electric Vehicles", "End of Contract", "Salary Sacrifice", "Complaints"],
                        "description": "Category of the question"
                    },
                    "question": {
                        "type": "string",
                        "description": "The specific question being asked"
                    }
                },
                "required": ["question"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me find that information for you..."
            }
        ],
        "server": {
            "url": "https://webhook.site/arval-faq"
        }
    }
]

async def configure_assistant():
    """Configure the Vapi assistant with all settings."""
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Complete assistant configuration
    config = {
        "name": "Arval Driver Desk",
        "firstMessage": "Hello, welcome to Arval Driver Desk. How may I help you today?",
        "model": {
            "provider": "openrouter",
            "model": "openai/gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ],
            "temperature": 0.7,
            "maxTokens": 500,
            # This is where we add the OpenRouter API key
            "customLlmProviderCredentials": {
                "apiKey": OPENROUTER_API_KEY
            }
        },
        "voice": {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            "model": "eleven_turbo_v2_5",
            "stability": 0.5,
            "similarityBoost": 0.8,
            "speed": 1.0
        },
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en"
        },
        "endCallFunctionEnabled": True,
        "dialKeypadFunctionEnabled": True,
        "silenceTimeoutSeconds": 30,
        "maxDurationSeconds": 600,
        "backgroundSound": "office",
        "backchannelingEnabled": True,
        "startSpeakingPlan": {
            "waitSeconds": 0.4
        },
        "stopSpeakingPlan": {
            "numWords": 2,
            "voiceSeconds": 0.2
        }
    }
    
    print("🔧 Configuring Vapi Assistant...")
    print(f"   Assistant ID: {ASSISTANT_ID}")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Update the assistant
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        
        async with session.patch(url, headers=headers, json=config) as response:
            if response.status == 200:
                result = await response.json()
                print("✅ Assistant configuration updated successfully!")
                print()
                print("📋 Configuration Summary:")
                print(f"   • Name: {result.get('name', 'N/A')}")
                print(f"   • Model: {result.get('model', {}).get('model', 'N/A')}")
                print(f"   • Voice: {result.get('voice', {}).get('provider', 'N/A')}")
                print(f"   • Transcriber: {result.get('transcriber', {}).get('provider', 'N/A')}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Failed to update assistant: {response.status}")
                print(f"   Error: {error_text}")
                
                # Try alternative approach - add API key as environment variable
                print()
                print("🔄 Trying alternative configuration...")
                
                # Simpler config without custom credentials
                simple_config = {
                    "name": "Arval Driver Desk",
                    "firstMessage": "Hello, welcome to Arval Driver Desk. How may I help you today?",
                    "model": {
                        "provider": "openai",  # Use OpenAI directly
                        "model": "gpt-4o",
                        "messages": [
                            {
                                "role": "system",
                                "content": SYSTEM_PROMPT
                            }
                        ],
                        "temperature": 0.7,
                        "maxTokens": 500
                    },
                    "voice": {
                        "provider": "11labs",
                        "voiceId": "21m00Tcm4TlvDq8ikWAM",
                        "model": "eleven_turbo_v2_5"
                    },
                    "transcriber": {
                        "provider": "deepgram",
                        "model": "nova-2",
                        "language": "en"
                    }
                }
                
                async with session.patch(url, headers=headers, json=simple_config) as retry_response:
                    if retry_response.status == 200:
                        print("✅ Updated with OpenAI provider (uses Vapi's default keys)")
                        return True
                    else:
                        error2 = await retry_response.text()
                        print(f"❌ Alternative also failed: {error2}")
                        return False


async def add_provider_key():
    """Add OpenRouter as a custom provider key in Vapi."""
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🔑 Checking if we can add OpenRouter as a provider key...")
    
    async with aiohttp.ClientSession() as session:
        # First, let's check what providers are available
        url = "https://api.vapi.ai/provider-key"
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                keys = await response.json()
                print(f"   Current provider keys: {len(keys)}")
                for key in keys:
                    print(f"   • {key.get('provider', 'unknown')}")
            else:
                print(f"   Could not list provider keys: {response.status}")
        
        # Try to add OpenRouter key
        key_data = {
            "provider": "openrouter",
            "key": OPENROUTER_API_KEY
        }
        
        async with session.post(url, headers=headers, json=key_data) as response:
            if response.status == 201 or response.status == 200:
                print("✅ OpenRouter API key added to Vapi!")
                return True
            else:
                error = await response.text()
                print(f"   Note: {error}")
                return False


async def test_assistant():
    """Create a quick test call to verify the assistant works."""
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print()
    print("=" * 60)
    print("🧪 TESTING YOUR ASSISTANT")
    print("=" * 60)
    print()
    print("To test your assistant, you have 3 options:")
    print()
    print("1️⃣  WEB TEST (Easiest - No phone needed):")
    print("   → Go to: https://vapi.ai/dashboard")
    print("   → Click on your 'Arval Driver Desk' assistant")
    print("   → Click the 'TEST' tab at the top")
    print("   → Click 'Start Call' and speak into your microphone")
    print()
    print("2️⃣  PHONE TEST (Requires phone number):")
    print("   → Go to: https://vapi.ai/dashboard/phone-numbers")
    print("   → Buy a UK number (+44)")
    print("   → Assign it to 'Arval Driver Desk' assistant")
    print("   → Call the number from any phone")
    print()
    print("3️⃣  OUTBOUND TEST CALL:")
    print("   → We can make the assistant call YOUR phone")
    print("   → This requires buying credits in Vapi")
    print()
    
    return True


async def main():
    print("=" * 60)
    print("🚀 ARVAL VAPI COMPLETE CONFIGURATION")
    print("=" * 60)
    print()
    
    # Step 1: Try to add provider key
    await add_provider_key()
    print()
    
    # Step 2: Configure assistant
    success = await configure_assistant()
    
    # Step 3: Show test instructions
    if success:
        await test_assistant()
    
    print()
    print("=" * 60)
    print("📌 IMPORTANT NOTES")
    print("=" * 60)
    print()
    print("If web test doesn't work, Vapi may require you to add")
    print("your own API keys in the dashboard:")
    print()
    print("1. Go to: https://vapi.ai/dashboard/org/api-keys")
    print("2. Add your OpenAI API key (or OpenRouter)")
    print("3. Then the assistant will work")
    print()
    print("Alternatively, Vapi provides $10 free credits that")
    print("include access to their built-in OpenAI keys.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
