# Postman Testing Guide - Client Need Service Agent

## Prerequisites

- Install Postman: https://www.postman.com/downloads/
- Server running on: `http://localhost:8000`

## Postman Collection Setup

### 1. Health Check

```
Method: GET
URL: http://localhost:8000/api/v1/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T..."
}
```

### 2. Start Conversation

```
Method: POST
URL: http://localhost:8000/api/v1/conversation/start
Headers: Content-Type: application/json
Body (raw JSON):
{
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "source_channel": "web"
}
```

**Expected Response:**

```json
{
  "conversation_id": "uuid-here",
  "client_need_id": "uuid-here",
  "greeting_message": "Hello! I'm here to help...",
  "audio_url": null
}
```

**Save the `conversation_id` for next requests!**

### 3. Send Message

```
Method: POST
URL: http://localhost:8000/api/v1/conversation/{conversation_id}/message
Headers: Content-Type: application/json
Body (raw JSON):
{
  "message": "I need a Python developer to build an e-commerce platform for 3 months",
  "message_type": "text"
}
```

**Expected Response:**

```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "assistant_message": "That sounds interesting...",
  "audio_url": null,
  "extraction_updates": [
    {
      "field_name": "project_type",
      "field_value": "web_development",
      "confidence": 0.9
    }
  ],
  "profile_completeness": 25,
  "missing_fields": ["budget_min", "timeline_duration_weeks"],
  "can_complete": false
}
```

### 4. Get Conversation Status

```
Method: GET
URL: http://localhost:8000/api/v1/conversation/{conversation_id}/status
```

### 5. Complete Conversation

```
Method: POST
URL: http://localhost:8000/api/v1/conversation/{conversation_id}/complete
```

### 6. List Client Needs

```
Method: GET
URL: http://localhost:8000/api/v1/client-needs?limit=10&offset=0
```

### 7. Get Specific Client Need

```
Method: GET
URL: http://localhost:8000/api/v1/client-needs/{client_need_id}
```

## Testing Without Azure/PostgreSQL

Since you don't have Azure and PostgreSQL set up yet, the actual conversation flow won't work, BUT you can:

1. **Test API Structure** - All endpoints are accessible
2. **Verify Request/Response Models** - See what data shapes are expected
3. **Check Error Handling** - See how errors are returned

## Next Steps to Make It Fully Functional

To get the full service working:

1. **Setup Azure OpenAI** (see docs/AZURE_SETUP.md)

   - Create Azure OpenAI resource
   - Deploy GPT-4 model
   - Get API key and endpoint

2. **Setup Azure Speech** (see docs/AZURE_SETUP.md)

   - Create Speech Service
   - Get API key

3. **Setup PostgreSQL**

   - Create a database (e.g. `client_needs_db`) and run `backend/client_need_service/db/schema.sql`
   - Set `DATABASE_URL` or `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` in `.env`

4. **Update .env** with real credentials

5. **Install Full Dependencies:**
   ```bash
   pip install openai azure-cognitiveservices-speech
   ```

Then the full conversational AI will work!
