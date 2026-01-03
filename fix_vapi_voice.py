#!/usr/bin/env python3
"""
Fix Vapi Voice Configuration
Switch to Vapi's built-in providers that work with free credits.
"""

import asyncio
import aiohttp
import json

VAPI_API_KEY = "e72c9335-54ce-4271-aac5-7c46598ed3ae"
ASSISTANT_ID = "b543468c-e12e-481f-abb6-d0e129c7e5bb"

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

## Key Services
- Personal Contract Hire (PCH)
- Business Contract Hire (BCH)
- Salary Sacrifice schemes (Ignition by Arval)
- Fleet Management
- Electric Vehicle solutions

Always end with "Is there anything else I can help you with?" and "Thank you for choosing Arval."
"""

async def fix_assistant():
    """Update assistant to use Vapi's built-in providers."""
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use Vapi's built-in providers that work with credits
    config = {
        "name": "Arval Driver Desk",
        "firstMessage": "Hello, welcome to Arval Driver Desk. How may I help you today?",
        "model": {
            "provider": "openai",
            "model": "gpt-4o-mini",  # Cheaper, faster model
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ],
            "temperature": 0.7,
            "maxTokens": 300
        },
        # Use Vapi's built-in voice (works with credits)
        "voice": {
            "provider": "vapi",
            "voiceId": "Elliot"  # Vapi's built-in voice
        },
        # Use Deepgram for transcription (works with credits)
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en"
        },
        "silenceTimeoutSeconds": 30,
        "maxDurationSeconds": 300,
        "endCallFunctionEnabled": False,  # Disable to simplify
        "backgroundSound": "off"  # Remove external URL dependency
    }
    
    print("=" * 60)
    print("🔧 FIXING VAPI ASSISTANT CONFIGURATION")
    print("=" * 60)
    print()
    print("Switching to Vapi's built-in providers...")
    print()
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        
        async with session.patch(url, headers=headers, json=config) as response:
            if response.status == 200:
                result = await response.json()
                print("✅ SUCCESS! Assistant updated!")
                print()
                print("📋 New Configuration:")
                print(f"   • Model: {result.get('model', {}).get('model', 'N/A')}")
                print(f"   • Voice: Vapi built-in (Elliot)")
                print(f"   • Transcriber: Deepgram Nova-2")
                print()
                print("=" * 60)
                print("🎤 NOW TRY TESTING AGAIN!")
                print("=" * 60)
                print()
                print("1. Go to: https://vapi.ai/dashboard")
                print("2. Click on 'Arval Driver Desk'")
                print("3. Click the 'TEST' tab")
                print("4. Click 'Start Call' and speak!")
                print()
                return True
            else:
                error = await response.text()
                print(f"❌ Failed: {response.status}")
                print(f"   Error: {error}")
                
                # Try with even simpler config
                print()
                print("🔄 Trying minimal configuration...")
                
                minimal_config = {
                    "name": "Arval Driver Desk",
                    "firstMessage": "Hello, welcome to Arval Driver Desk. How may I help you today?",
                    "model": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "system", 
                                "content": "You are Arval Driver Desk assistant. Help callers with vehicle leasing questions. Be friendly and helpful. Arval is a vehicle leasing company owned by BNP Paribas."
                            }
                        ]
                    },
                    "voice": {
                        "provider": "playht",
                        "voiceId": "jennifer"
                    },
                    "transcriber": {
                        "provider": "deepgram",
                        "model": "nova-2",
                        "language": "en"
                    }
                }
                
                async with session.patch(url, headers=headers, json=minimal_config) as retry:
                    if retry.status == 200:
                        print("✅ Minimal config applied successfully!")
                        print()
                        print("Now try testing again in the dashboard.")
                        return True
                    else:
                        error2 = await retry.text()
                        print(f"❌ Minimal config also failed: {error2}")
                        return False


async def check_available_voices():
    """Check what voices are available."""
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print()
    print("🔍 Checking available voice providers...")
    
    async with aiohttp.ClientSession() as session:
        # Get current assistant config
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"   Current voice provider: {data.get('voice', {}).get('provider', 'None')}")
                print(f"   Current transcriber: {data.get('transcriber', {}).get('provider', 'None')}")


async def main():
    await check_available_voices()
    await fix_assistant()


if __name__ == "__main__":
    asyncio.run(main())
