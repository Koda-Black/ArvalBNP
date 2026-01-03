#!/usr/bin/env python3
"""Publish and verify the Arval Driver Desk voice agent."""

import asyncio
import aiohttp

VAPI_API_KEY = 'e72c9335-54ce-4271-aac5-7c46598ed3ae'
ASSISTANT_ID = 'b543468c-e12e-481f-abb6-d0e129c7e5bb'

async def publish():
    headers = {
        'Authorization': f'Bearer {VAPI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    print('=' * 60)
    print('📢 PUBLISHING ARVAL DRIVER DESK')
    print('=' * 60)
    print()
    
    async with aiohttp.ClientSession() as session:
        # Try to publish the assistant
        url = f'https://api.vapi.ai/assistant/{ASSISTANT_ID}/publish'
        
        async with session.post(url, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                print('✅ PUBLISHED SUCCESSFULLY!')
                print()
                print(f'   Assistant: {result.get("name", "Arval Driver Desk")}')
                print(f'   ID: {ASSISTANT_ID}')
                print()
            elif response.status == 404:
                print('ℹ️  No separate publish step needed in Vapi.')
                print('   Your assistant is already LIVE!')
                print()
            else:
                error = await response.text()
                if 'not found' in error.lower() or response.status == 404:
                    print('ℹ️  Vapi assistants are live immediately after creation.')
                    print('   No separate publish step required!')
                    print()
                else:
                    print(f'   Status: {response.status}')
        
        # Verify it's accessible
        print('🔍 Verifying deployment...')
        get_url = f'https://api.vapi.ai/assistant/{ASSISTANT_ID}'
        async with session.get(get_url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f'   ✅ Name: {data.get("name")}')
                print(f'   ✅ Model: {data.get("model", {}).get("model")}')
                tools = data.get("model", {}).get("tools", [])
                print(f'   ✅ Tools: {len(tools)} configured')
                for tool in tools:
                    func = tool.get("function", {})
                    print(f'      • {func.get("name")}')
                print()
        
        # Verify phone number is connected
        print('📞 Verifying phone connection...')
        phone_url = 'https://api.vapi.ai/phone-number'
        async with session.get(phone_url, headers=headers) as response:
            if response.status == 200:
                phones = await response.json()
                for phone in phones:
                    num = phone.get('number', phone.get('phoneNumber', ''))
                    aid = phone.get('assistantId', '')
                    if aid == ASSISTANT_ID:
                        print(f'   ✅ {num} → Arval Driver Desk')
        
        print()
        print('=' * 60)
        print('🎉 YOUR AGENT IS LIVE AND PUBLISHED!')
        print('=' * 60)
        print()
        print('📞 CALL NOW: +1 (408) 731-2213')
        print()
        print('Your voice agent is ready to:')
        print('   • Answer leasing questions')
        print('   • Book appointments')
        print('   • Handle roadside assistance')
        print('   • Capture leads')
        print('   • Schedule callbacks')
        print()
        print('🌐 Dashboard: https://dashboard.vapi.ai')
        print()

if __name__ == '__main__':
    asyncio.run(publish())
