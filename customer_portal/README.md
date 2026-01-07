# Customer Portal

This portal allows customers to access their voice agent data **without** having access to your Vapi dashboard.

## Features

- 📞 **Call Transcripts** - View all calls with full transcripts
- 📅 **Appointments** - See all booked appointments
- 👥 **Leads** - Access captured lead information
- 📊 **Analytics** - Call volume, duration, trends
- 📤 **Export** - Download data as JSON or CSV

## Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn aiohttp pyjwt python-dotenv
```

### 2. Configure Customer API Keys

Edit `api.py` and add customers to the `CUSTOMERS` dictionary:

```python
CUSTOMERS = {
    "arval": {
        "api_key": "arval_secret_api_key_123",  # Generate a unique key
        "assistant_id": "b543468c-e12e-481f-abb6-d0e129c7e5bb",
        "company_name": "Arval BNP Paribas",
        "phone_numbers": ["+14087312213"]
    },
    "another_company": {
        "api_key": "another_company_key_456",
        "assistant_id": "their-assistant-id",
        "company_name": "Another Company",
        "phone_numbers": ["+1555555555"]
    }
}
```

### 3. Run the Portal

```bash
python customer_portal/api.py
```

Or with uvicorn:
```bash
uvicorn customer_portal.api:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access Documentation

Open http://localhost:8000/docs for interactive API documentation.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/calls` | GET | List all calls with transcripts |
| `/calls/{id}` | GET | Get detailed call information |
| `/appointments` | GET | List all appointments |
| `/leads` | GET | List all captured leads |
| `/analytics` | GET | Get call analytics |
| `/export/calls` | GET | Export calls as JSON/CSV |

## Authentication

Customers authenticate using an API key in the header:

```bash
curl -H "X-API-Key: arval_secret_api_key_123" http://localhost:8000/calls
```

## Customer Access Options

### Option 1: Direct API Access
Give customers their API key and endpoint URL. They can integrate with their own systems.

### Option 2: White-label Dashboard
Build a simple web dashboard (React/Vue) that calls this API. Host it for customers.

### Option 3: Embed in Their Portal
Provide embed code or iframe for customers to add to their existing portals.

## Security Best Practices

1. **Use HTTPS** in production
2. **Generate unique API keys** per customer
3. **Rate limit** API requests
4. **Log all access** for audit
5. **Rotate keys** periodically

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY customer_portal/ ./customer_portal/
CMD ["uvicorn", "customer_portal.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Options
- **Railway.app** - Easy Python hosting
- **Render.com** - Free tier available
- **AWS Lambda + API Gateway** - Serverless
- **DigitalOcean App Platform** - Simple deployment
