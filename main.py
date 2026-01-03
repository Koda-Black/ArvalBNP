"""
Arval BNP Paribas Voice Agent
Main entry point for the voice agent application.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from agent.voice_agent import ArvalVoiceAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to run the Arval Voice Agent."""
    print("\n" + "=" * 60)
    print("🚗 Welcome to Arval BNP Paribas Voice Agent")
    print("=" * 60)
    print("\nI'm here to help you with:")
    print("  • Vehicle leasing inquiries")
    print("  • MOT and service appointments")
    print("  • Fleet management questions")
    print("  • Roadside assistance")
    print("  • And much more!")
    print("\nType 'quit' or 'exit' to end the conversation.")
    print("-" * 60 + "\n")

    # Check for OpenRouter API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key.startswith("your_"):
        print("⚠️  Warning: OPENROUTER_API_KEY not configured.")
        print("Please set your OpenRouter API key in the .env file.")
        print("Get one at: https://openrouter.ai/\n")
        return

    # Initialize the voice agent
    try:
        agent = ArvalVoiceAgent(
            api_key=api_key,
            model_id=os.getenv("MODEL_ID", "openai/gpt-4o-mini")
        )
        
        # Run the interactive conversation loop
        await agent.run_conversation()
        
    except KeyboardInterrupt:
        print("\n\nGoodbye! Thank you for choosing Arval BNP Paribas. 🚗")
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
