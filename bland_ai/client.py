"""
Bland AI Integration for Arval BNP Voice Agent
Deploy the voice agent to Bland AI platform for phone calls.
"""

import os
import json
import aiohttp
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Bland AI API Configuration
BLAND_API_BASE_URL = "https://api.bland.ai/v1"


class BlandAIClient:
    """Client for interacting with Bland AI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Bland AI client.
        
        Args:
            api_key: Bland AI API key. If not provided, reads from BLAND_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("BLAND_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Bland AI API key not provided. Set BLAND_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to Bland AI API."""
        url = f"{BLAND_API_BASE_URL}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, 
                url, 
                headers=self.headers, 
                json=data
            ) as response:
                result = await response.json()
                
                if response.status >= 400:
                    raise Exception(f"Bland AI API error: {result}")
                
                return result
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new agent in Bland AI.
        
        Args:
            agent_config: Agent configuration dictionary
            
        Returns:
            Created agent details
        """
        return await self._make_request("POST", "agents", agent_config)
    
    async def update_agent(self, agent_id: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing agent."""
        return await self._make_request("POST", f"agents/{agent_id}", agent_config)
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent details."""
        return await self._make_request("GET", f"agents/{agent_id}")
    
    async def list_agents(self) -> Dict[str, Any]:
        """List all agents."""
        return await self._make_request("GET", "agents")
    
    async def make_call(
        self,
        phone_number: str,
        agent_id: Optional[str] = None,
        task: Optional[str] = None,
        first_sentence: Optional[str] = None,
        wait_for_greeting: bool = True,
        record: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Initiate an outbound call.
        
        Args:
            phone_number: Phone number to call (E.164 format)
            agent_id: ID of the agent to use
            task: Task/prompt for the call
            first_sentence: First thing the agent says
            wait_for_greeting: Wait for the person to speak first
            record: Whether to record the call
            
        Returns:
            Call details including call_id
        """
        data = {
            "phone_number": phone_number,
            "wait_for_greeting": wait_for_greeting,
            "record": record,
            **kwargs
        }
        
        if agent_id:
            data["agent_id"] = agent_id
        if task:
            data["task"] = task
        if first_sentence:
            data["first_sentence"] = first_sentence
        
        return await self._make_request("POST", "calls", data)
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Get call details and transcript."""
        return await self._make_request("GET", f"calls/{call_id}")
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End an ongoing call."""
        return await self._make_request("POST", f"calls/{call_id}/stop")


def load_system_prompt() -> str:
    """Load the system prompt from SYSTEM_CONTEXT.md."""
    context_path = Path(__file__).parent.parent / "SYSTEM_CONTEXT.md"
    
    if context_path.exists():
        with open(context_path, "r", encoding="utf-8") as f:
            return f.read()
    
    return ""


def load_faqs() -> str:
    """Load FAQ content for the agent."""
    faqs = {
        "Vehicle Leasing": {
            "What is full-service vehicle leasing?": "Full-service leasing includes the vehicle, maintenance, insurance, road tax, and breakdown cover in one monthly payment. No hidden costs!",
            "How long are typical lease terms?": "Lease terms typically range from 24 to 48 months, depending on your needs.",
            "Can I lease electric vehicles?": "Absolutely! We're committed to sustainability and offer a wide range of EVs.",
        },
        "Fleet Management": {
            "What fleet sizes do you work with?": "We work with fleets of all sizes - from small businesses with a few vehicles to large corporations with thousands.",
            "How many vehicles does Arval manage?": "We manage over 190,000 vehicles in the UK and 1.82 million globally across 28 countries.",
        },
        "MOT & Service": {
            "How do I book an MOT?": "Simply call our Driver Desk and we'll arrange everything for you.",
            "Is MOT included in my lease?": "Yes, MOT is typically included in our full-service lease packages.",
        },
        "Business Hours": {
            "What are your hours?": "Our Driver Desk is open Monday to Friday, 9:00 AM to 5:00 PM GMT.",
            "Do you have 24/7 support?": "Yes, our emergency roadside assistance is available 24/7.",
        },
    }
    
    faq_text = "## Frequently Asked Questions\n\n"
    for category, questions in faqs.items():
        faq_text += f"### {category}\n"
        for q, a in questions.items():
            faq_text += f"**Q: {q}**\nA: {a}\n\n"
    
    return faq_text


def get_arval_agent_config() -> Dict[str, Any]:
    """
    Get the complete Bland AI agent configuration for Arval.
    
    Returns:
        Agent configuration dictionary ready for Bland AI API
    """
    system_context = load_system_prompt()
    faqs = load_faqs()
    
    return {
        "name": "Arval Driver Desk Agent",
        
        # Main prompt/task for the agent
        "prompt": f"""You are the official voice agent for Arval BNP Paribas Group, a global leader in vehicle leasing and the fourth largest leasing company in the UK.

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

{faqs}

## Additional Context
{system_context[:3000]}  

Always maintain a professional yet friendly demeanor. If you cannot help with something, offer to schedule a callback or transfer to the appropriate team.""",

        # Voice settings
        "voice": "maya",  # Options: maya, mason, ryan, adriana, tina, etc.
        "voice_settings": {
            "speed": 1.0,        # 0.5 to 2.0 (1.0 is normal)
            "stability": 0.7,   # 0.0 to 1.0 (higher = more consistent)
        },
        
        # First sentence when answering calls
        "first_sentence": "Hello, thank you for calling Arval Driver Desk. My name is Maya, how can I help you today?",
        
        # Model settings
        "model": "enhanced",  # Options: base, enhanced, turbo
        "temperature": 0.7,
        
        # Call handling settings
        "wait_for_greeting": True,
        "record": True,
        "max_duration": 1800,  # 30 minutes max
        
        # Interruption handling
        "interruption_threshold": 100,  # Lower = more interruptible
        
        # Language
        "language": "en-GB",  # British English
        
        # Transfer settings (if needed)
        "transfer_phone_number": None,  # Set to human agent number if needed
        
        # Webhook for call events (optional)
        "webhook": None,  # Set to your webhook URL
        
        # Analysis prompt for post-call summary
        "analysis_prompt": """Analyze this call and extract:
1. Customer name and contact details if provided
2. The main reason for the call
3. Any appointments booked (type, date, time)
4. Any leads captured (company, fleet size, interests)
5. Action items or follow-ups needed
6. Customer satisfaction indicators""",

        # Pathway/conversation flow (optional structured flow)
        "pathway_id": None,  # Can use Bland AI pathway builder
    }


def get_voice_options() -> Dict[str, str]:
    """
    Get available voice options for Bland AI.
    
    Returns:
        Dictionary of voice names and descriptions
    """
    return {
        # Female voices
        "maya": "Professional female voice (British accent available) - Recommended",
        "adriana": "Warm female voice with slight accent",
        "tina": "Friendly, energetic female voice",
        "nicole": "Calm, professional female voice",
        "emma": "Natural British female voice",
        
        # Male voices
        "mason": "Professional male voice",
        "ryan": "Friendly male voice",
        "josh": "Young, casual male voice",
        "david": "Mature, authoritative male voice",
        "james": "British male voice",
    }


async def deploy_agent(api_key: Optional[str] = None) -> str:
    """
    Deploy the Arval voice agent to Bland AI.
    
    Args:
        api_key: Bland AI API key (optional, uses env var if not provided)
        
    Returns:
        Agent ID of the deployed agent
    """
    client = BlandAIClient(api_key)
    config = get_arval_agent_config()
    
    logger.info("Deploying Arval Voice Agent to Bland AI...")
    result = await client.create_agent(config)
    
    agent_id = result.get("agent_id")
    logger.info(f"Agent deployed successfully! Agent ID: {agent_id}")
    
    return agent_id


async def test_call(
    phone_number: str, 
    agent_id: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Make a test call with the deployed agent.
    
    Args:
        phone_number: Phone number to call (E.164 format, e.g., +447123456789)
        agent_id: ID of the deployed Bland AI agent
        api_key: Bland AI API key (optional)
        
    Returns:
        Call details
    """
    client = BlandAIClient(api_key)
    
    result = await client.make_call(
        phone_number=phone_number,
        agent_id=agent_id,
        wait_for_greeting=True,
        record=True
    )
    
    logger.info(f"Test call initiated! Call ID: {result.get('call_id')}")
    return result


# CLI for deployment
if __name__ == "__main__":
    import asyncio
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Arval Voice Agent to Bland AI")
    parser.add_argument("--deploy", action="store_true", help="Deploy the agent")
    parser.add_argument("--test-call", type=str, help="Make a test call to this phone number")
    parser.add_argument("--agent-id", type=str, help="Agent ID for test calls")
    parser.add_argument("--show-config", action="store_true", help="Show agent configuration")
    parser.add_argument("--voices", action="store_true", help="Show available voices")
    
    args = parser.parse_args()
    
    if args.show_config:
        config = get_arval_agent_config()
        print(json.dumps(config, indent=2))
    
    elif args.voices:
        print("\n🎤 Available Voices for Bland AI:\n")
        for voice, desc in get_voice_options().items():
            print(f"  • {voice}: {desc}")
        print("\nRecommendation: Use 'maya' or 'emma' for British English customer service.")
    
    elif args.deploy:
        agent_id = asyncio.run(deploy_agent())
        print(f"\n✅ Agent deployed! Agent ID: {agent_id}")
        print(f"\nSave this ID in your .env file as: BLAND_AGENT_ID={agent_id}")
    
    elif args.test_call:
        if not args.agent_id:
            print("Error: --agent-id required for test calls")
        else:
            result = asyncio.run(test_call(args.test_call, args.agent_id))
            print(f"\n📞 Test call initiated!")
            print(f"Call ID: {result.get('call_id')}")
    
    else:
        parser.print_help()
