"""
Vapi AI Integration for Arval BNP Voice Agent
Alternative to Bland AI - More globally accessible.
Deploy the voice agent to Vapi AI platform for phone calls.

Sign up at: https://vapi.ai/
"""

import os
import json
import aiohttp
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Vapi API Configuration
VAPI_API_BASE_URL = "https://api.vapi.ai"


class VapiClient:
    """Client for interacting with Vapi AI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Vapi AI client.
        
        Args:
            api_key: Vapi API key. If not provided, reads from VAPI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("VAPI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Vapi API key not provided. Set VAPI_API_KEY environment variable "
                "or pass api_key parameter.\n"
                "Get your key at: https://dashboard.vapi.ai/"
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to Vapi API."""
        url = f"{VAPI_API_BASE_URL}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, 
                url, 
                headers=self.headers, 
                json=data
            ) as response:
                result = await response.json()
                
                if response.status >= 400:
                    raise Exception(f"Vapi API error: {result}")
                
                return result
    
    async def create_assistant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new assistant in Vapi."""
        return await self._make_request("POST", "assistant", config)
    
    async def update_assistant(self, assistant_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing assistant."""
        return await self._make_request("PATCH", f"assistant/{assistant_id}", config)
    
    async def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """Get assistant details."""
        return await self._make_request("GET", f"assistant/{assistant_id}")
    
    async def list_assistants(self) -> List[Dict[str, Any]]:
        """List all assistants."""
        return await self._make_request("GET", "assistant")
    
    async def create_phone_number(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create/buy a phone number."""
        return await self._make_request("POST", "phone-number", config)
    
    async def make_call(
        self,
        phone_number: str,
        assistant_id: str,
        customer_number: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Initiate an outbound call.
        
        Args:
            phone_number: Your Vapi phone number to call from
            assistant_id: ID of the assistant to use
            customer_number: Customer's phone number to call
            
        Returns:
            Call details including call_id
        """
        data = {
            "phoneNumberId": phone_number,
            "assistantId": assistant_id,
            "customer": {
                "number": customer_number
            },
            **kwargs
        }
        
        return await self._make_request("POST", "call/phone", data)
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Get call details and transcript."""
        return await self._make_request("GET", f"call/{call_id}")


def load_system_prompt() -> str:
    """Load the system prompt from SYSTEM_CONTEXT.md."""
    context_path = Path(__file__).parent.parent / "SYSTEM_CONTEXT.md"
    
    if context_path.exists():
        with open(context_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Truncate if too long
            return content[:4000] if len(content) > 4000 else content
    
    return ""


def get_arval_vapi_config() -> Dict[str, Any]:
    """
    Get the Vapi assistant configuration for Arval.
    
    Returns:
        Assistant configuration dictionary ready for Vapi API
    """
    system_prompt = load_system_prompt()
    
    return {
        "name": "Arval Driver Desk Agent",
        
        # Model configuration
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.7,
            "systemPrompt": f"""You are the official voice agent for Arval BNP Paribas Group, a global leader in vehicle leasing and the fourth largest leasing company in the UK.

## Your Role
You serve as the first point of contact for customers calling the Driver Desk, handling a wide variety of queries with warmth and professionalism.

## Key Responsibilities
1. Answer questions about Arval services, vehicle leasing, fleet management
2. Help customers book MOT appointments, service appointments, and consultations
3. Handle after-hours inquiries with callbacks and emergency info
4. Capture lead information from prospective customers

## Communication Style
- Be warm, friendly, and helpful - more human than corporate
- Use natural conversational language, no scripts
- Take your time to understand customer needs
- Always aim for the right outcome for the customer

## Important Company Information
- Fleet size: Over 190,000 vehicles in the UK
- Services: Full-service vehicle leasing, EV solutions, fleet management
- Location: Swindon, Wiltshire, UK
- Business Hours: Monday-Friday, 9:00 AM - 5:00 PM GMT
- Emergency Roadside Assistance: Available 24/7

## FAQs

### Vehicle Leasing
- Full-service leasing includes vehicle, maintenance, insurance, road tax, and breakdown cover
- Lease terms: 24 to 48 months
- We offer a wide range of electric vehicles

### MOT & Service
- MOT is included in full-service lease packages
- Call Driver Desk to book appointments

### Business Hours
- Monday to Friday: 9:00 AM - 5:00 PM GMT
- 24/7 Emergency Roadside Assistance available

{system_prompt[:2000]}

Always maintain a professional yet friendly demeanor. If you cannot help, offer to schedule a callback."""
        },
        
        # Voice configuration
        "voice": {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel - professional female
            "stability": 0.7,
            "similarityBoost": 0.75,
        },
        
        # First message
        "firstMessage": "Hello, thank you for calling Arval Driver Desk. My name is Rachel, how can I help you today?",
        
        # End call settings
        "endCallMessage": "Thank you for calling Arval. Have a great day!",
        
        # Transcriber settings
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en-GB",
        },
        
        # Call settings
        "silenceTimeoutSeconds": 30,
        "maxDurationSeconds": 1800,  # 30 minutes
        "backgroundSound": "office",
        
        # Recording
        "recordingEnabled": True,
        
        # Voicemail detection
        "voicemailDetection": {
            "enabled": True,
            "provider": "twilio"
        }
    }


def get_vapi_voice_options() -> Dict[str, Dict[str, str]]:
    """
    Get available voice options for Vapi.
    
    Returns:
        Dictionary of voice providers and their options
    """
    return {
        "11labs": {
            "rachel": {"id": "21m00Tcm4TlvDq8ikWAM", "desc": "Professional female (Recommended)"},
            "drew": {"id": "29vD33N1CtxCmqQRPOHJ", "desc": "Professional male"},
            "clyde": {"id": "2EiwWnXFnvU5JabPnv8n", "desc": "Friendly male"},
            "domi": {"id": "AZnzlk1XvdvUeBnXmlld", "desc": "Expressive female"},
            "bella": {"id": "EXAVITQu4vr4xnSDxMaL", "desc": "Soft female"},
        },
        "playht": {
            "jennifer": {"id": "jennifer", "desc": "American female"},
            "will": {"id": "will", "desc": "American male"},
        },
        "deepgram": {
            "asteria": {"id": "asteria", "desc": "Female voice"},
            "luna": {"id": "luna", "desc": "Female voice"},
            "stella": {"id": "stella", "desc": "Female voice"},
            "orion": {"id": "orion", "desc": "Male voice"},
        }
    }


async def deploy_vapi_assistant(api_key: Optional[str] = None) -> str:
    """
    Deploy the Arval voice assistant to Vapi.
    
    Args:
        api_key: Vapi API key (optional, uses env var if not provided)
        
    Returns:
        Assistant ID of the deployed assistant
    """
    client = VapiClient(api_key)
    config = get_arval_vapi_config()
    
    logger.info("Deploying Arval Voice Assistant to Vapi...")
    result = await client.create_assistant(config)
    
    assistant_id = result.get("id")
    logger.info(f"Assistant deployed successfully! ID: {assistant_id}")
    
    return assistant_id


# CLI for deployment
if __name__ == "__main__":
    import asyncio
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Arval Voice Agent to Vapi AI")
    parser.add_argument("--deploy", action="store_true", help="Deploy the assistant")
    parser.add_argument("--show-config", action="store_true", help="Show assistant configuration")
    parser.add_argument("--voices", action="store_true", help="Show available voices")
    
    args = parser.parse_args()
    
    if args.show_config:
        config = get_arval_vapi_config()
        print(json.dumps(config, indent=2))
    
    elif args.voices:
        print("\n🎤 Available Voices for Vapi AI:\n")
        for provider, voices in get_vapi_voice_options().items():
            print(f"\n{provider.upper()}:")
            for name, info in voices.items():
                print(f"  • {name}: {info['desc']}")
        print("\nRecommendation: Use '11labs/rachel' for professional customer service.")
    
    elif args.deploy:
        assistant_id = asyncio.run(deploy_vapi_assistant())
        print(f"\n✅ Assistant deployed! ID: {assistant_id}")
        print(f"\nSave this ID in your .env file as: VAPI_ASSISTANT_ID={assistant_id}")
    
    else:
        parser.print_help()
