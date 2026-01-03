#!/usr/bin/env python3
"""
Add tools to Vapi assistant using the correct API endpoint.
Tools must be created separately and then attached to the assistant.
"""

import asyncio
import aiohttp
import json

VAPI_API_KEY = "e72c9335-54ce-4271-aac5-7c46598ed3ae"
ASSISTANT_ID = "b543468c-e12e-481f-abb6-d0e129c7e5bb"

# Tool definitions in Vapi format
TOOLS_TO_CREATE = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment or meeting for the customer. Use this when customer wants to schedule a meeting, consultation, MOT, service, or any appointment with Arval.",
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
                    "appointment_type": {
                        "type": "string",
                        "description": "Type of appointment: Leasing Consultation, MOT, Service, Fleet Consultation, or Sales Demo"
                    },
                    "preferred_date": {
                        "type": "string",
                        "description": "Preferred date for the appointment"
                    },
                    "preferred_time": {
                        "type": "string",
                        "description": "Preferred time for the appointment"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes or vehicle interests"
                    }
                },
                "required": ["customer_name", "customer_phone", "appointment_type"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me book that appointment for you now."
            },
            {
                "type": "request-complete",
                "content": "I've scheduled your appointment. You'll receive a confirmation call from our team. Is there anything else I can help you with?"
            },
            {
                "type": "request-failed",
                "content": "I'm having trouble booking right now. Please call 0370 419 7000 directly."
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture contact details for customers interested in vehicle leasing services.",
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
                    "interest": {
                        "type": "string",
                        "description": "What they're interested in"
                    },
                    "company_name": {
                        "type": "string",
                        "description": "Company name if business inquiry"
                    }
                },
                "required": ["contact_name", "phone", "interest"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "Let me save your details."
            },
            {
                "type": "request-complete",
                "content": "Thank you! A specialist will contact you within 24 hours. Is there anything else?"
            }
        ]
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_callback",
            "description": "Schedule a callback for the customer when they prefer to be called back.",
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
                        "description": "When to call back"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for callback"
                    }
                },
                "required": ["customer_name", "phone_number", "reason"]
            }
        },
        "messages": [
            {
                "type": "request-start",
                "content": "I'll schedule that callback."
            },
            {
                "type": "request-complete",
                "content": "Done! Our team will call you back. Anything else I can help with?"
            }
        ]
    }
]


async def add_tools_to_assistant():
    """Add tools to the Vapi assistant."""
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("=" * 70)
    print("🔧 ADDING TOOLS TO VAPI ASSISTANT")
    print("=" * 70)
    print()
    
    async with aiohttp.ClientSession() as session:
        # First, let's check what endpoints are available for tools
        # Try to get current assistant config
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                current = await response.json()
                print(f"✅ Current assistant: {current.get('name')}")
                print(f"   Model: {current.get('model', {}).get('model')}")
                print(f"   Current tools: {len(current.get('tools', []))}")
                print()
            else:
                print(f"❌ Could not get assistant: {response.status}")
                return
        
        # Now try adding tools via the model.tools property
        print("📦 Adding tools via model configuration...")
        
        # Tools need to be in the model object for some Vapi versions
        model_config = current.get('model', {})
        model_config['tools'] = TOOLS_TO_CREATE
        
        update_payload = {
            "model": model_config
        }
        
        async with session.patch(url, headers=headers, json=update_payload) as response:
            if response.status == 200:
                result = await response.json()
                model_tools = result.get('model', {}).get('tools', [])
                print(f"✅ SUCCESS! {len(model_tools)} tools added!")
                for tool in model_tools:
                    if 'function' in tool:
                        print(f"   • {tool['function'].get('name')}")
                return True
            else:
                error = await response.text()
                print(f"❌ Model tools failed: {error}")
        
        # Try alternative: toolIds approach
        print()
        print("🔄 Trying to create tools separately...")
        
        tool_ids = []
        for tool_def in TOOLS_TO_CREATE:
            # Create tool
            create_url = "https://api.vapi.ai/tool"
            async with session.post(create_url, headers=headers, json=tool_def) as response:
                if response.status in [200, 201]:
                    created = await response.json()
                    tool_id = created.get('id')
                    tool_ids.append(tool_id)
                    print(f"   ✅ Created: {tool_def['function']['name']} ({tool_id})")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed to create {tool_def['function']['name']}: {error}")
        
        if tool_ids:
            # Attach tools to assistant
            print()
            print(f"🔗 Attaching {len(tool_ids)} tools to assistant...")
            
            attach_payload = {
                "toolIds": tool_ids
            }
            
            async with session.patch(url, headers=headers, json=attach_payload) as response:
                if response.status == 200:
                    print("✅ Tools attached successfully!")
                    return True
                else:
                    error = await response.text()
                    print(f"❌ Failed to attach: {error}")
        
        print()
        print("=" * 70)
        print("ℹ️  NOTE: Vapi's free tier may not support custom tools.")
        print("=" * 70)
        print()
        print("However, your assistant NOW has the full knowledge base and will:")
        print("  • Give crisp, informed responses about Arval")
        print("  • Collect customer details verbally")
        print("  • Direct them to call 0370 419 7000 for bookings")
        print()
        print("For full tool functionality, you may need to:")
        print("  1. Add tools manually in the Vapi dashboard")
        print("  2. Or upgrade to a paid Vapi plan")
        print()
        
        return False


async def main():
    await add_tools_to_assistant()


if __name__ == "__main__":
    asyncio.run(main())
