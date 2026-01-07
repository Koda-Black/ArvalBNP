# Voice Agent Replication Prompt

Copy this entire prompt and paste it into a new chat to create a voice agent for any company.

---

## 🚀 THE PROMPT

```
CREATE A PROFESSIONAL VOICE AGENT FOR THE FOLLOWING COMPANY:

**COMPANY NAME:** [INSERT COMPANY NAME HERE]

**BUSINESS DESCRIPTION:** [INSERT WHAT THE COMPANY DOES - e.g., "A vehicle leasing company that provides fleet management, personal contract hire, and salary sacrifice schemes for businesses and individuals in the UK"]

---

## REQUIREMENTS

Build a complete voice agent with the following specifications:

### 1. PROJECT SETUP
- Python project with virtual environment
- Use OpenRouter API for model access (GPT-4o)
- Use Vapi AI for voice deployment
- Organize code into: agent/, models/, customer_portal/, data/, tests/

### 2. VOICE CONFIGURATION
- Pick a professional female voice from Vapi's available voices (Lily, Kylie, Savannah, Hana, Neha, Paige, Leah, Tara, Jess, Mia, or Zoe)
- Set welcome message: "Welcome to [COMPANY NAME]! My name is [VOICE NAME], how may I help you?"
- Configure end-call detection with phrases like "goodbye", "bye", "that's all", "no thanks"
- Set silence timeout to 30 seconds
- Set max call duration to 30 minutes

### 3. AGENT PERSONALITY
Create an empathetic, energetic, professional personality that:
- Shows genuine care for every caller
- Sounds positive and engaged (never monotone)
- Keeps responses clear, apt, and focused
- Always provides a solution or next step
- Gives direct answers without rambling

### 4. CRITICAL BEHAVIOR RULES
The agent must NEVER say "I don't have that information". Instead:
- Offer to connect with a specialist team
- Offer to schedule a callback
- Provide the main contact number

If callers deviate from company-related topics:
- Politely redirect: "I appreciate your question, but [COMPANY NAME] specializes in [SERVICES]. Is there anything about [RELEVANT TOPIC] I can assist with today?"

### 5. TOOLS TO IMPLEMENT (10 TOTAL)
1. **book_appointment** - Schedule appointments (service, consultation, demo, etc.)
2. **capture_lead** - Capture prospective customer information
3. **schedule_callback** - Schedule callback requests
4. **get_roadside_assistance** - Emergency/urgent support info (if applicable)
5. **get_business_hours** - Provide operating hours
6. **check_after_hours** - Check if calling outside business hours
7. **get_faq_answer** - Answer common questions
8. **book_calendly_appointment** - Direct Calendly integration for instant booking
9. **transfer_call** - Transfer to specific departments
10. **send_sms_confirmation** - Send appointment details via text

### 6. SYSTEM CONTEXT
Go online and research the company thoroughly to gather:
- Company history, founding date, parent company
- All office locations with full addresses
- All contact numbers (main, sales, support, emergency)
- All services offered with descriptions
- Department names and what they handle
- Leadership team (if public)
- Key statistics (employees, customers, coverage area)
- FAQs covering at least 30 common questions

Organize this into a SYSTEM_CONTEXT.md file with sections:
- Company Overview
- UK/Regional Offices (with full addresses)
- Contact Numbers
- Departments
- Services
- FAQs by Category

### 7. ENVIRONMENT VARIABLES
Create .env.example with:
- OPENROUTER_API_KEY
- VAPI_API_KEY
- VAPI_ASSISTANT_ID
- CALENDLY_API_KEY
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER

### 8. CUSTOMER PORTAL
Create a FastAPI customer portal that allows the company to:
- View all call transcripts
- View appointments booked
- View leads captured
- See analytics (call volume, duration, trends)
- Export data as JSON/CSV

### 9. DEPLOYMENT SCRIPT
Create deploy_v2.py that:
- Configures the Vapi assistant with all settings
- Sets the voice, greeting, and personality
- Adds all 10 tools
- Configures end-call detection
- Verifies phone number assignment
- Prints success confirmation with phone number

### 10. DOCUMENTATION
Create:
- README.md with project overview, setup instructions, usage
- SETUP_GUIDE.md with step-by-step deployment guide
- .gitignore excluding .env, venv/, __pycache__/

### 11. FILE STRUCTURE
```
project/
├── .env.example
├── .gitignore
├── README.md
├── SETUP_GUIDE.md
├── SYSTEM_CONTEXT.md
├── deploy_v2.py
├── main.py
├── requirements.txt
├── pyproject.toml
├── agent/
│   ├── __init__.py
│   ├── tools.py
│   └── voice_agent.py
├── models/
│   ├── __init__.py
│   ├── appointment.py
│   └── lead.py
├── customer_portal/
│   ├── api.py
│   └── README.md
├── data/
│   └── .gitkeep
├── tests/
│   ├── __init__.py
│   └── test_agent.py
└── vapi_ai/
    ├── __init__.py
    └── client.py
```

### 12. CLEAN PROJECT
Remove any redundant files. Keep only:
- Core agent code
- Single deployment script (deploy_v2.py)
- Customer portal
- Documentation
- Configuration files

---

## EXECUTION STEPS

1. Create the project folder structure
2. Research the company online for comprehensive information
3. Create SYSTEM_CONTEXT.md with all gathered info
4. Implement all 10 tools in agent/tools.py
5. Create the deployment script
6. Create the customer portal API
7. Create documentation
8. Set up virtual environment and install dependencies
9. Test locally
10. Deploy to Vapi
11. Verify deployment and test the phone number
12. Push to GitHub (ensure .env is in .gitignore)

---

## QUALITY CHECKLIST

Before completing, verify:
- [ ] All 10 tools implemented
- [ ] SYSTEM_CONTEXT.md has 30+ FAQs
- [ ] All office locations included
- [ ] All contact numbers included
- [ ] Voice is female and professional
- [ ] End-call detection configured
- [ ] Customer portal working
- [ ] No redundant files
- [ ] .env is gitignored
- [ ] Deployment successful
- [ ] Phone number assigned and callable

---

NOW BUILD THIS COMPLETE VOICE AGENT PROJECT.
```

---

## 📋 USAGE INSTRUCTIONS

1. Copy everything between the triple backticks above
2. Replace `[INSERT COMPANY NAME HERE]` with the company name
3. Replace `[INSERT WHAT THE COMPANY DOES...]` with a brief description
4. Paste into a new chat
5. The AI will build the complete project

## 💡 EXAMPLE FILLED IN

```
**COMPANY NAME:** TechFleet Solutions

**BUSINESS DESCRIPTION:** A technology equipment leasing company that provides laptop, server, and IT infrastructure leasing solutions for businesses in the United States. They offer flexible lease terms, asset management, and end-of-life disposal services.
```

## 🔧 AFTER BUILDING

1. Get API keys:
   - OpenRouter: https://openrouter.ai
   - Vapi: https://vapi.ai
   - Calendly: https://calendly.com/integrations
   - Twilio (for SMS): https://twilio.com

2. Add keys to `.env` file

3. Run deployment:
   ```bash
   source venv/bin/activate
   python deploy_v2.py
   ```

4. Test the phone number

5. Set up customer portal for the client
