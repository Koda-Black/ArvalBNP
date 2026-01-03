"""
Setup Vapi Tools for Arval Voice Agent (using aiohttp)
This script adds all the required tools/functions to your Vapi assistant.
"""

import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

# Vapi API endpoint
VAPI_API_URL = f"https://api.vapi.ai/assistant/{VAPI_ASSISTANT_ID}"

# Define all the tools for the Arval Voice Agent
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for a customer. Use this when a customer wants to schedule an MOT, service, inspection, fleet consultation, or sales demo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "The customer's full name"
                    },
                    "contact_phone": {
                        "type": "string",
                        "description": "The customer's phone number"
                    },
                    "contact_email": {
                        "type": "string",
                        "description": "The customer's email address"
                    },
                    "appointment_type": {
                        "type": "string",
                        "enum": ["MOT", "Service", "Inspection", "Fleet Consultation", "Sales Demo"],
                        "description": "The type of appointment to book"
                    },
                    "preferred_date": {
                        "type": "string",
                        "description": "The preferred date for the appointment in YYYY-MM-DD format"
                    },
                    "preferred_time": {
                        "type": "string",
                        "enum": ["Morning (9-12)", "Afternoon (12-3)", "Late Afternoon (3-5)"],
                        "description": "The preferred time slot for the appointment"
                    },
                    "vehicle_registration": {
                        "type": "string",
                        "description": "The vehicle registration number (optional)"
                    },
                    "additional_notes": {
                        "type": "string",
                        "description": "Any additional notes about the appointment (optional)"
                    }
                },
                "required": ["customer_name", "contact_phone", "appointment_type", "preferred_date", "preferred_time"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me book that appointment for you..."
            },
            {
                "type": "request-complete",
                "content": "I've scheduled your appointment. You'll receive a confirmation shortly."
            },
            {
                "type": "request-failed",
                "content": "I'm sorry, I couldn't complete the booking right now. Would you like me to schedule a callback instead?"
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture lead information from a prospective customer interested in fleet leasing or vehicle services. Use this when someone expresses interest in leasing vehicles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {
                        "type": "string",
                        "description": "The prospect's full name"
                    },
                    "contact_email": {
                        "type": "string",
                        "description": "The prospect's email address"
                    },
                    "contact_phone": {
                        "type": "string",
                        "description": "The prospect's phone number"
                    },
                    "company_name": {
                        "type": "string",
                        "description": "The company name for business inquiries"
                    },
                    "current_fleet_size": {
                        "type": "integer",
                        "description": "The current number of vehicles in their fleet"
                    },
                    "projected_fleet_size": {
                        "type": "integer",
                        "description": "The projected fleet size after leasing"
                    },
                    "vehicle_interests": {
                        "type": "string",
                        "description": "Specific vehicle types or models of interest"
                    },
                    "timeline": {
                        "type": "string",
                        "description": "Decision timeline (e.g., 'Within 1 month', '3-6 months')"
                    },
                    "preferred_contact_method": {
                        "type": "string",
                        "enum": ["Phone", "Email", "Either"],
                        "description": "The preferred method of contact"
                    },
                    "inquiry_notes": {
                        "type": "string",
                        "description": "Additional notes about the inquiry"
                    }
                },
                "required": ["contact_name", "contact_phone"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me capture your details..."
            },
            {
                "type": "request-complete",
                "content": "Thank you! I've recorded your interest and one of our fleet specialists will be in touch with you shortly."
            },
            {
                "type": "request-failed",
                "content": "I'm sorry, I couldn't save your details. Let me take note and have someone call you back."
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_callback",
            "description": "Schedule a callback request for the customer. Use this when a customer wants to be called back later or when it's after business hours.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "The customer's full name"
                    },
                    "contact_phone": {
                        "type": "string",
                        "description": "The phone number to call back"
                    },
                    "preferred_time": {
                        "type": "string",
                        "description": "Preferred callback time: 'Morning', 'Afternoon', 'ASAP', or a specific time"
                    },
                    "callback_reason": {
                        "type": "string",
                        "description": "Brief description of what the callback is regarding"
                    },
                    "is_urgent": {
                        "type": "boolean",
                        "description": "Whether this is an urgent matter requiring priority callback"
                    }
                },
                "required": ["customer_name", "contact_phone", "callback_reason"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me schedule that callback for you..."
            },
            {
                "type": "request-complete",
                "content": "I've scheduled a callback for you. One of our team members will call you back."
            },
            {
                "type": "request-failed",
                "content": "I couldn't schedule the callback, but I've made a note. Someone will get back to you as soon as possible."
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "get_roadside_assistance",
            "description": "Provide emergency roadside assistance information. Use this when a customer has broken down or needs emergency help with their vehicle.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "messages": [
            {
                "type": "request-complete",
                "content": "For immediate roadside assistance, our 24/7 emergency line is available. If you're in a safe location, please call the number provided in your vehicle documents. If this is an emergency and you're in danger, please call 999 immediately. Our roadside assistance team can help with breakdowns, flat tyres, and getting you back on the road."
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "get_business_hours",
            "description": "Get the current business hours for Arval Driver Desk. Use this when a customer asks about opening hours or when they can call.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "messages": [
            {
                "type": "request-complete",
                "content": "Our Driver Desk is available Monday to Friday, 9 AM to 5 PM GMT. For emergency roadside assistance, we're available 24/7. Outside business hours, I can still help with FAQs, schedule callbacks, or capture your details for our team to follow up."
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "check_after_hours",
            "description": "Check if it's currently after business hours and provide appropriate guidance. Use this when you need to determine if the office is open.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "messages": [
            {
                "type": "request-complete",
                "content": "Our office hours are Monday to Friday, 9 AM to 5 PM GMT. If you're calling outside these hours, I can still help you with general questions, schedule a callback for when we're open, or connect you with our 24/7 roadside assistance if it's an emergency."
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "get_faq_answer",
            "description": "Get answers to frequently asked questions about Arval services. Use this when a customer has general questions about leasing, EVs, maintenance, or contracts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["leasing", "fleet", "ev", "mot", "pricing", "contracts", "maintenance", "salary_sacrifice", "general"],
                        "description": "The topic of the FAQ question"
                    },
                    "specific_question": {
                        "type": "string",
                        "description": "The specific question the customer is asking"
                    }
                },
                "required": ["topic"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me find that information for you..."
            },
            {
                "type": "request-complete",
                "content": "Based on your question, here's what I can tell you..."
            }
        ]
    }
]


async def update_assistant_with_tools():
    """Update the Vapi assistant with all the tools."""
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # The update payload with tools
    payload = {
        "model": {
            "provider": "openrouter",
            "model": "openai/gpt-4o",
            "tools": TOOLS,
            "toolIds": []
        }
    }
    
    print("🔧 Updating Vapi Assistant with tools...")
    print(f"   Assistant ID: {VAPI_ASSISTANT_ID}")
    print(f"   Adding {len(TOOLS)} tools...")
    
    async with aiohttp.ClientSession() as session:
        async with session.patch(VAPI_API_URL, headers=headers, json=payload) as response:
            result = await response.text()
            
            if response.status == 200:
                print("\n✅ SUCCESS! All tools have been added to your Vapi assistant!")
                print("\nTools configured:")
                for tool in TOOLS:
                    print(f"   • {tool['function']['name']}")
                
                print("\n🎯 Next steps:")
                print("   1. Go to https://dashboard.vapi.ai/")
                print("   2. Click on your 'Arval Driver Desk' assistant")
                print("   3. Go to the TOOLS tab to verify")
                print("   4. Use the TEST tab to try your agent")
                print("   5. Buy a phone number to receive real calls")
                
                return True
            else:
                print(f"\n❌ Error: {response.status}")
                print(result)
                return False


if __name__ == "__main__":
    if not VAPI_API_KEY:
        print("❌ Error: VAPI_API_KEY not found in .env file")
        exit(1)
    
    if not VAPI_ASSISTANT_ID:
        print("❌ Error: VAPI_ASSISTANT_ID not found in .env file")
        exit(1)
    
    asyncio.run(update_assistant_with_tools())
