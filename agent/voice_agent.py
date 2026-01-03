"""
Arval BNP Paribas Voice Agent
Core agent implementation using OpenAI SDK with function calling.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional
from openai import AsyncOpenAI

from .tools import (
    book_appointment,
    capture_lead,
    get_business_hours,
    check_after_hours,
    get_roadside_assistance,
    schedule_callback,
    get_faq_answer,
)

logger = logging.getLogger(__name__)


def load_system_context() -> str:
    """Load the system context from the markdown file."""
    context_path = Path(__file__).parent.parent / "SYSTEM_CONTEXT.md"
    
    if context_path.exists():
        with open(context_path, "r", encoding="utf-8") as f:
            return f.read()
    
    # Fallback system prompt if file not found
    return """You are a helpful voice agent for Arval BNP Paribas Group, 
    a global leader in vehicle leasing. Help customers with inquiries, 
    appointments, and lead capture."""


AGENT_INSTRUCTIONS = """You are the official voice agent for Arval BNP Paribas Group, a global leader in vehicle leasing and the fourth largest leasing company in the UK.

## Your Role
You serve as the first point of contact for customers calling the Driver Desk, handling a wide variety of queries with warmth and professionalism.

## Key Responsibilities
1. **Answer Questions** - Provide accurate information about Arval services, vehicle leasing, fleet management, and company policies.
2. **Book Appointments** - Help customers schedule MOT appointments, service appointments, fleet consultations, and vehicle inspections.
3. **Handle After-Hours** - During non-business hours (outside Mon-Fri 9AM-5PM GMT), offer appropriate alternatives and schedule callbacks.
4. **Capture Leads** - Collect information from prospective customers interested in fleet leasing or vehicle services.

## Communication Style
- Be warm, friendly, and helpful - more human than corporate
- Take your time to understand customer needs - there are no time limits on calls
- Use natural conversational language, no scripts
- Always aim for the right outcome for the customer
- Be patient and thorough in your responses

## Important Information
- Fleet size: Over 190,000 vehicles in the UK
- Services: Full-service vehicle leasing, EV solutions, fleet management
- Location: Swindon, Wiltshire, UK (Hybrid working)
- Business Hours: Monday-Friday, 9:00 AM - 5:00 PM GMT
- Emergency Roadside Assistance: Available 24/7

Always maintain a professional yet friendly demeanor, representing the Arval brand positively. If you cannot help with something, offer to connect the customer with the appropriate team or schedule a callback.
"""

# Define tools for function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for a customer (MOT, Service, Inspection, Fleet Consultation, or Sales Demo)",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "The full name of the customer"},
                    "contact_phone": {"type": "string", "description": "Customer's phone number"},
                    "contact_email": {"type": "string", "description": "Customer's email address"},
                    "appointment_type": {"type": "string", "enum": ["MOT", "Service", "Inspection", "Fleet Consultation", "Sales Demo"], "description": "Type of appointment"},
                    "preferred_date": {"type": "string", "description": "Preferred date in YYYY-MM-DD format"},
                    "preferred_time": {"type": "string", "enum": ["Morning (9-12)", "Afternoon (12-3)", "Late Afternoon (3-5)"], "description": "Preferred time slot"},
                    "vehicle_registration": {"type": "string", "description": "Vehicle registration number (optional)"},
                    "additional_notes": {"type": "string", "description": "Any additional notes (optional)"}
                },
                "required": ["customer_name", "contact_phone", "contact_email", "appointment_type", "preferred_date", "preferred_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture lead information from a prospective customer interested in fleet leasing or vehicle services",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {"type": "string", "description": "Full name of the prospective customer"},
                    "contact_email": {"type": "string", "description": "Email address for follow-up"},
                    "contact_phone": {"type": "string", "description": "Phone number for follow-up"},
                    "company_name": {"type": "string", "description": "Company name (for business inquiries)"},
                    "current_fleet_size": {"type": "integer", "description": "Current number of vehicles in fleet"},
                    "projected_fleet_size": {"type": "integer", "description": "Projected fleet size after leasing"},
                    "current_provider": {"type": "string", "description": "Current leasing provider, if any"},
                    "vehicle_interests": {"type": "string", "description": "Specific vehicle types or models of interest"},
                    "timeline": {"type": "string", "description": "Decision timeline (e.g., 'Within 1 month', '3-6 months')"},
                    "budget_range": {"type": "string", "description": "Budget considerations or range"},
                    "preferred_contact_method": {"type": "string", "enum": ["Phone", "Email", "Either"], "description": "Preferred method of contact"},
                    "inquiry_notes": {"type": "string", "description": "Additional notes about the inquiry"}
                },
                "required": ["contact_name", "contact_email", "contact_phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_business_hours",
            "description": "Get the current business hours for Arval Driver Desk",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_after_hours",
            "description": "Check if it's currently after business hours and provide appropriate guidance",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_roadside_assistance",
            "description": "Provide emergency roadside assistance information for breakdowns or emergencies",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_callback",
            "description": "Schedule a callback request for the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "The customer's full name"},
                    "contact_phone": {"type": "string", "description": "Phone number to call back"},
                    "preferred_time": {"type": "string", "description": "Preferred callback time: 'Morning', 'Afternoon', 'ASAP', or specific time"},
                    "callback_reason": {"type": "string", "description": "Brief description of what the callback is regarding"},
                    "is_urgent": {"type": "boolean", "description": "Whether this is an urgent matter requiring priority callback"}
                },
                "required": ["customer_name", "contact_phone", "preferred_time", "callback_reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_faq_answer",
            "description": "Get answers to frequently asked questions about Arval services",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "enum": ["leasing", "fleet", "ev", "mot", "pricing", "contracts", "careers", "general"], "description": "The topic of the FAQ question"}
                },
                "required": ["topic"]
            }
        }
    }
]

# Map function names to actual functions
FUNCTION_MAP = {
    "book_appointment": book_appointment,
    "capture_lead": capture_lead,
    "get_business_hours": get_business_hours,
    "check_after_hours": check_after_hours,
    "get_roadside_assistance": get_roadside_assistance,
    "schedule_callback": schedule_callback,
    "get_faq_answer": get_faq_answer,
}


class ArvalVoiceAgent:
    """Voice agent for Arval BNP Paribas customer service."""
    
    def __init__(self, api_key: str, model_id: str = "openai/gpt-4o-mini"):
        """
        Initialize the Arval Voice Agent.
        
        Args:
            api_key: OpenRouter API key for model access
            model_id: The model ID to use (default: openai/gpt-4o-mini)
        """
        self.api_key = api_key
        self.model_id = model_id
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://arval.co.uk",
                "X-Title": "Arval Voice Agent"
            }
        )
        self.conversation_history = []
        self.system_context = load_system_context()
        
        logger.info(f"Initializing Arval Voice Agent with model: {model_id}")
    
    def _get_system_message(self) -> dict:
        """Get the system message with instructions and context."""
        return {
            "role": "system",
            "content": f"{AGENT_INSTRUCTIONS}\n\n## Company Knowledge Base\n{self.system_context}"
        }
    
    async def _execute_function(self, function_name: str, arguments: dict) -> str:
        """Execute a function and return the result."""
        if function_name not in FUNCTION_MAP:
            return f"Error: Unknown function {function_name}"
        
        try:
            func = FUNCTION_MAP[function_name]
            result = func(**arguments)
            return result
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            return f"Error executing {function_name}: {str(e)}"
    
    async def process_message(self, user_input: str) -> str:
        """
        Process a single user message and return the agent's response.
        
        Args:
            user_input: The user's message
            
        Returns:
            The agent's response text
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Build messages with system context
        messages = [self._get_system_message()] + self.conversation_history
        
        try:
            # Call the model with tools
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=2048,
            )
            
            assistant_message = response.choices[0].message
            
            # Handle tool calls if any
            if assistant_message.tool_calls:
                # Add assistant message with tool calls to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    result = await self._execute_function(function_name, arguments)
                    
                    # Add tool result to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                
                # Get final response after tool execution
                messages = [self._get_system_message()] + self.conversation_history
                final_response = await self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                    max_tokens=2048,
                )
                
                final_message = final_response.choices[0].message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_message
                })
                
                return final_message
            else:
                # No tool calls, just return the response
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content
                })
                return assistant_message.content
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I apologize, but I'm experiencing a technical issue. Please try again or call our Driver Desk directly."
    
    async def run_conversation(self):
        """Run an interactive conversation loop."""
        # Initial greeting
        greeting = await self.process_message(
            "Please greet me as a customer calling Arval's Driver Desk. Keep it brief and friendly."
        )
        print(f"Agent: {greeting}\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                    farewell = await self.process_message(
                        "The customer is ending the call. Please give a warm goodbye."
                    )
                    print(f"\nAgent: {farewell}")
                    break
                
                # Process the user's message
                response = await self.process_message(user_input)
                print(f"\nAgent: {response}\n")
                
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n")
                break
        
        print("\nThank you for choosing Arval BNP Paribas! 🚗")
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation for handoff or logging."""
        user_messages = [m for m in self.conversation_history if m.get("role") == "user"]
        return f"Conversation with {len(user_messages)} customer messages."
