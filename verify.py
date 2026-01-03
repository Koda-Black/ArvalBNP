#!/usr/bin/env python3
"""Verify final configuration"""

import asyncio
import aiohttp

VAPI_API_KEY = 'e72c9335-54ce-4271-aac5-7c46598ed3ae'
ASSISTANT_ID = 'b543468c-e12e-481f-abb6-d0e129c7e5bb'

async def verify():
    headers = {
        'Authorization': f'Bearer {VAPI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        url = f'https://api.vapi.ai/assistant/{ASSISTANT_ID}'
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print('=' * 60)
                print('✅ FINAL CONFIGURATION')
                print('=' * 60)
                print()
                print(f'Name: {data.get("name")}')
                print(f'First Message: {data.get("firstMessage", "")[:60]}...')
                print()
                print('Model:')
                model = data.get('model', {})
                print(f'  Provider: {model.get("provider")}')
                print(f'  Model: {model.get("model")}')
                print()
                tools = model.get('tools', [])
                print(f'Tools: {len(tools)}')
                for t in tools:
                    if 'function' in t:
                        print(f'  - {t["function"].get("name")}')
                print()
                print(f'Voice: {data.get("voice", {}).get("voiceId")}')
                print(f'Transcriber: {data.get("transcriber", {}).get("model")}')
                print()
                messages = model.get('messages', [])
                if messages:
                    content = messages[0].get('content', '')
                    if 'Arval' in content:
                        print('System prompt: Contains Arval knowledge')
                    else:
                        print('System prompt: May be missing knowledge')
                print()
                print('=' * 60)
                print('TEST YOUR ASSISTANT NOW!')
                print('=' * 60)
                print()
                print('1. Go to: https://vapi.ai/dashboard')
                print('2. Click "Arval Driver Desk"')
                print('3. Click "TEST" tab')
                print('4. Say: "I want to book a meeting with your team"')
                print()
                print('The assistant should now:')
                print('  - Ask for your name')
                print('  - Ask for your phone number')
                print('  - Confirm the appointment')
                print('  - Use the book_appointment tool')

asyncio.run(verify())
