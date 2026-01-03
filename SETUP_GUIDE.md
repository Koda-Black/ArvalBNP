# Arval BNP Voice Agent - Setup Guide

This guide walks you through setting up the Arval Voice Agent for local testing and deploying to Bland AI for production phone calls.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting Your GitHub Token](#getting-your-github-token)
3. [Local Setup](#local-setup)
4. [Running the Agent Locally](#running-the-agent-locally)
5. [Deploying to Bland AI](#deploying-to-bland-ai)
6. [Voice Settings Configuration](#voice-settings-configuration)
7. [Adding FAQs](#adding-faqs)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.9+** installed on your system
- A **GitHub account** (free)
- A **Bland AI account** (for voice deployment)

---

## Getting Your GitHub Token

The GitHub token allows access to AI models for free. Here's how to get one:

### Step-by-Step:

1. **Go to GitHub Token Settings**

   - Visit: https://github.com/settings/tokens
   - Or: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate a New Token**
   - Click **"Generate new token"** → **"Generate new token (classic)"**
3. **Configure the Token**

   - **Note**: Give it a descriptive name like `Arval Voice Agent`
   - **Expiration**: Choose your preferred duration (90 days recommended)
   - **Scopes**: No special scopes needed! Just leave defaults.

4. **Generate and Copy**

   - Click **"Generate token"**
   - ⚠️ **IMPORTANT**: Copy the token immediately! You won't see it again.
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

5. **Save to .env File**
   ```bash
   cd /Users/macbook/Desktop/Personal-Projects/ArvalBNP
   cp .env.example .env
   # Edit .env and paste your token
   ```

---

## Local Setup

### 1. Navigate to the Project

```bash
cd /Users/macbook/Desktop/Personal-Projects/ArvalBNP
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install openai python-dotenv aiohttp
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your favorite editor and add your GitHub token:

```
GITHUB_TOKEN=ghp_your_actual_token_here
```

---

## Running the Agent Locally

### Interactive Mode

```bash
source venv/bin/activate
python main.py
```

You'll see:

```
============================================================
🚗 Welcome to Arval BNP Paribas Voice Agent
============================================================

I'm here to help you with:
  • Vehicle leasing inquiries
  • MOT and service appointments
  • Fleet management questions
  ...

Agent: Hello! Thank you for calling Arval Driver Desk...

You: [type your message here]
```

### Example Conversations

```
You: I want to book an MOT
Agent: I'd be happy to help you book an MOT appointment! Could you please provide me with your name, phone number, and preferred date?

You: What are your business hours?
Agent: Our Driver Desk is open Monday to Friday, 9:00 AM to 5:00 PM GMT...

You: I'm interested in leasing 50 vehicles for my company
Agent: That's fantastic! I'd love to help you explore our fleet leasing options...
```

---

## Deploying to Bland AI

Bland AI provides phone numbers and handles real voice calls.

### 1. Create a Bland AI Account

1. Visit https://www.bland.ai/
2. Click **"Get Started"** or **"Sign Up"**
3. Complete registration
4. Add payment method (pay-per-call pricing)

### 2. Get Your API Key

1. Go to Bland AI Dashboard: https://app.bland.ai/
2. Navigate to **Settings** → **API Keys**
3. Click **"Create API Key"**
4. Copy the key to your `.env` file:
   ```
   BLAND_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 3. Deploy Your Agent

```bash
source venv/bin/activate
python -m bland_ai.client --deploy
```

You'll receive an Agent ID. Save it to your `.env`:

```
BLAND_AGENT_ID=agent_xxxxxxxxxxxxxxxx
```

### 4. Get a Phone Number

1. In Bland AI Dashboard, go to **Phone Numbers**
2. Click **"Buy Number"**
3. Choose your country (UK: +44)
4. Select a number and purchase
5. Link it to your Agent ID

### 5. Make a Test Call

```bash
python -m bland_ai.client --test-call "+447123456789" --agent-id "your_agent_id"
```

---

## Voice Settings Configuration

### Changing the Voice

Edit `bland_ai/client.py` and modify the `get_arval_agent_config()` function:

```python
# Voice options for British customer service:
"voice": "maya",  # or "emma" for British female voice
```

### Available Voices

| Voice   | Description         | Best For                            |
| ------- | ------------------- | ----------------------------------- |
| `maya`  | Professional female | Default, great for customer service |
| `emma`  | British female      | UK-focused businesses               |
| `tina`  | Friendly female     | Casual interactions                 |
| `mason` | Professional male   | Corporate calls                     |
| `james` | British male        | UK-focused, formal                  |

### Adjusting Voice Settings

```python
"voice_settings": {
    "speed": 1.0,       # 0.5 (slow) to 2.0 (fast)
    "stability": 0.7,   # Higher = more consistent tone
}
```

### Customizing the Greeting

```python
"first_sentence": "Hello, thank you for calling Arval Driver Desk. My name is Maya, how can I help you today?"
```

---

## Adding FAQs

### Method 1: Edit SYSTEM_CONTEXT.md

Add your FAQs directly to the knowledge base:

```markdown
## Additional FAQs

### Topic: [Your Topic]

**Q: Your question here?**
A: Your answer here.
```

### Method 2: Edit the FAQ Tool

Edit `agent/tools.py` and find the `get_faq_answer` function:

```python
faqs = {
    "leasing": """...""",
    "your_new_topic": """**Your Topic FAQs:**

**Q: New question?**
A: New answer here.

**Q: Another question?**
A: Another answer here.""",
}
```

### Method 3: Bland AI Dashboard

1. Go to Bland AI Dashboard
2. Navigate to your Agent
3. Edit the prompt directly
4. Add FAQ sections to the prompt

---

## Project Structure

```
ArvalBNP/
├── main.py                    # Run locally
├── SYSTEM_CONTEXT.md          # Company knowledge base
├── .env                       # Your secrets (git-ignored)
├── agent/
│   ├── voice_agent.py         # Core AI agent
│   └── tools.py               # Appointment, lead, FAQ tools
├── bland_ai/
│   ├── client.py              # Bland AI deployment
│   └── webhook.py             # Handle call events
├── models/
│   ├── appointment.py
│   └── lead.py
└── data/                      # Stored appointments & leads
```

---

## Troubleshooting

### "pip: command not found"

Use `pip3` instead of `pip`:

```bash
pip3 install openai python-dotenv aiohttp
```

### "GITHUB_TOKEN not configured"

Make sure you:

1. Created `.env` file from `.env.example`
2. Added your actual token (not the placeholder)

### "Model not found" error

The model ID might be incorrect. Try:

```
MODEL_ID=openai/gpt-4o
```

### Bland AI: "Unauthorized"

Check that your `BLAND_API_KEY` is correct and has credits.

### Agent not responding correctly

1. Check `SYSTEM_CONTEXT.md` for accurate company info
2. Review the prompt in `bland_ai/client.py`
3. Test locally first before deploying

---

## Support

- **Local Issues**: Check the terminal output for error messages
- **Bland AI Issues**: Check their docs at https://docs.bland.ai/
- **GitHub Models**: Check https://github.com/marketplace/models

---

## Quick Reference

### Start Local Agent

```bash
cd /Users/macbook/Desktop/Personal-Projects/ArvalBNP
source venv/bin/activate
python main.py
```

### Deploy to Bland AI

```bash
python -m bland_ai.client --deploy
```

### Show Voice Options

```bash
python -m bland_ai.client --voices
```

### Show Agent Config

```bash
python -m bland_ai.client --show-config
```
