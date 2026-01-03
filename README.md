# Arval BNP Paribas Voice Agent

A Python-based voice agent for Arval BNP Paribas Group that handles customer inquiries, appointment booking, after-hours support, and lead capture.

## Features

- 🎤 **Voice Interaction** - Natural language processing for voice-based conversations
- ❓ **Q&A Support** - Answers questions about Arval services, fleet management, and vehicle leasing
- 📅 **Appointment Booking** - Schedule MOT, service appointments, and consultations
- 🌙 **After-Hours Handling** - 24/7 availability with intelligent routing
- 📋 **Lead Capture** - Collect and qualify prospective customer information

## Tech Stack

- **Python 3.10+**
- **Microsoft Agent Framework** - For building the AI agent
- **OpenAI/GitHub Models** - GPT-4.1 for natural language understanding
- **asyncio** - For asynchronous operations

## Installation

### Prerequisites

- Python 3.10 or higher
- GitHub Personal Access Token (PAT) for model access

### Setup

1. **Clone or navigate to the project directory:**

   ```bash
   cd /Users/macbook/Desktop/Personal-Projects/ArvalBNP
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**

   ```bash
   pip install agent-framework-azure-ai --pre
   pip install python-dotenv
   ```

   > ⚠️ Note: The `--pre` flag is required while Agent Framework is in preview.

4. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your GitHub token:

   ```
   GITHUB_TOKEN=your_github_personal_access_token
   ```

## Usage

### Running the Voice Agent

```bash
python main.py
```

### Interactive Mode

The agent runs in an interactive conversation mode where you can:

- Ask questions about Arval services
- Book appointments
- Request callbacks
- Inquire about vehicle leasing options

### Example Conversations

```
You: I'd like to book an MOT for my company car.
Agent: I'd be happy to help you book an MOT appointment. Could you please provide me with your vehicle registration number and preferred date for the appointment?

You: What are your business hours?
Agent: Our Driver Desk team is available Monday to Friday from 9:00 AM to 5:00 PM GMT. For emergency roadside assistance, we have 24/7 support available.

You: I'm interested in fleet leasing for my company.
Agent: That's great! I'd love to help you explore our fleet leasing options. To better assist you, could you tell me a bit about your company and how many vehicles you're looking to lease?
```

## Project Structure

```
ArvalBNP/
├── README.md              # This file
├── SYSTEM_CONTEXT.md      # Agent system context and company info
├── .env.example           # Environment variables template
├── .env                   # Your environment variables (git-ignored)
├── main.py                # Main application entry point
├── agent/
│   ├── __init__.py
│   ├── voice_agent.py     # Core voice agent implementation
│   └── tools.py           # Agent tools (booking, leads, etc.)
├── models/
│   ├── __init__.py
│   ├── appointment.py     # Appointment data models
│   └── lead.py            # Lead capture data models
├── data/
│   ├── appointments.json  # Stored appointments
│   └── leads.json         # Captured leads
└── tests/
    └── test_agent.py      # Unit tests
```

## Configuration

### Environment Variables

| Variable       | Description                                   | Required |
| -------------- | --------------------------------------------- | -------- |
| `GITHUB_TOKEN` | GitHub Personal Access Token for model access | Yes      |
| `MODEL_ID`     | AI model to use (default: `openai/gpt-4.1`)   | No       |
| `LOG_LEVEL`    | Logging level (default: `INFO`)               | No       |

## Tools

The agent has access to the following tools:

1. **book_appointment** - Schedule MOT, service, or consultation appointments
2. **capture_lead** - Collect prospective customer information
3. **get_business_hours** - Check current operating hours
4. **check_after_hours** - Determine if it's currently after hours
5. **get_roadside_assistance** - Provide emergency contact information
6. **schedule_callback** - Request a callback from the team

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Adding New Tools

1. Add the tool function in `agent/tools.py`
2. Include proper type annotations and docstrings
3. Register the tool in the agent configuration

## License

Proprietary - Arval BNP Paribas Group

## Support

For technical issues, please contact the development team.
For business inquiries, visit [arval.co.uk](https://www.arval.co.uk)
