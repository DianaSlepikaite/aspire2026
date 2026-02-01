# Client Need Agent - Testing Guide

## Overview

The Client Need Agent is a multi-agent system that processes unstructured client briefs and extracts structured client needs using AI.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT INPUT                          │
│  (Email, PDF, Text, Audio describing project needs)     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│         DATA INGESTION SERVICE                           │
│  • Extracts text from PDF/Audio                          │
│  • Normalizes content                                    │
│  • Creates audit trail                                   │
│  • Stores intake package                                 │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│      NEED EXTRACTION SERVICE                             │
│  • Analyzes text using Azure OpenAI                      │
│  • Extracts structured fields (19+ fields)               │
│  • Normalizes enum values                                │
│  • Calculates completeness score                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│        CLIENT NEED AGENT                                 │
│  • Orchestrates the extraction process                   │
│  • Stores client need in database                        │
│  • Analyzes missing information                          │
│  • Generates AI summary                                  │
│  • Suggests clarifying questions                         │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints

### 1. Data Ingestion Endpoints

#### Upload Text
```bash
POST /api/v1/intake/upload/text
Content-Type: multipart/form-data

Fields:
  - text_content (required): The client brief text
  - client_name (optional): Client's name
  - client_email (optional): Client's email
  - source_label (optional): Label for the source (e.g., "Email", "Chat")
  - tags (optional): Comma-separated tags

Response: ClientIntakePackage with id
```

#### Upload PDF
```bash
POST /api/v1/intake/upload/pdf
Content-Type: multipart/form-data

Fields:
  - file (required): PDF file
  - client_name (optional): Client's name
  - client_email (optional): Client's email
  - tags (optional): Comma-separated tags

Response: ClientIntakePackage with id
```

#### Upload Audio
```bash
POST /api/v1/intake/upload/audio
Content-Type: multipart/form-data

Fields:
  - file (required): Audio file (WAV, MP3)
  - client_name (optional): Client's name
  - client_email (optional): Client's email
  - language (optional): Language code (default: en-US)
  - tags (optional): Comma-separated tags

Response: ClientIntakePackage with id
```

### 2. Agent Endpoint

#### Process Intake
```bash
POST /api/v1/agent/process-intake
Content-Type: application/json

Body:
{
  "intake_id": "uuid-of-intake-package",
  "user_query": "optional context or questions"
}

Response:
{
  "output": "AI-generated summary with clarifying questions",
  "intermediate_steps": [
    {
      "step": "retrieve_intake",
      "action": "Retrieved intake package",
      "details": { ... }
    },
    ...
  ]
}
```

#### Ask Clarifying Questions
```bash
POST /api/v1/agent/clarifying-questions
Content-Type: application/json

Body:
{
  "client_need_id": "uuid-of-client-need",
  "context": "optional additional context"
}

Response: AI-generated clarifying questions
```

### 3. Client Need Endpoints

#### Get Client Need
```bash
GET /api/v1/client-needs/{id}

Response: Complete ClientNeed object with all extracted fields
```

## Extracted Fields

The agent extracts the following structured fields:

### Client Information
- `client_name`
- `client_email`
- `client_phone`
- `client_company`

### Project Details
- `project_title`
- `project_description`
- `project_type` (web development, mobile app, etc.)
- `industry`
- `key_challenges` (array)

### Skills
- `required_skills` (array)
- `preferred_skills` (array)
- `skill_level` (junior, mid, senior, expert)
- `certifications_required` (array)

### Budget
- `budget_min`
- `budget_max`
- `budget_currency`
- `budget_type` (hourly, fixed, monthly)

### Timeline
- `timeline_duration_weeks`
- `timeline_start_date`
- `timeline_end_date`
- `timeline_flexibility` (flexible, somewhat_flexible, strict)

### Urgency & Priority
- `urgency_level` (low, medium, high, critical)
- `priority_score` (1-10)

### Work Arrangement
- `work_location` (remote, onsite, hybrid)
- `work_location_details`
- `work_hours_requirement`

### Additional
- `team_size_needed`
- `collaboration_tools` (array)
- `communication_preferences`

## Testing Methods

### Method 1: Using the Test Script

```bash
cd /Users/jyokatra/Documents/ASPIRE2026/aspire2026/backend

./test_client_brief.sh "Client Name" "email@example.com" "I need a web application that..."
```

### Method 2: Manual cURL Commands

```bash
# Step 1: Ingest the client brief
INTAKE_ID=$(curl -X POST http://localhost:8000/api/v1/intake/upload/text \
  -F "text_content=Your client brief here..." \
  -F "client_name=John Doe" \
  -F "client_email=john@example.com" | jq -r '.id')

# Step 2: Process through agent
curl -X POST http://localhost:8000/api/v1/agent/process-intake \
  -H "Content-Type: application/json" \
  -d "{\"intake_id\": \"$INTAKE_ID\"}" | jq .

# Step 3: Get structured client need (extract client_need_id from step 2 response)
curl http://localhost:8000/api/v1/client-needs/{client_need_id} | jq .
```

### Method 3: Swagger UI

1. Navigate to http://localhost:8000/docs
2. Test endpoints interactively:
   - POST /api/v1/intake/upload/text
   - POST /api/v1/agent/process-intake
   - GET /api/v1/client-needs/{id}

## Example Test Scenarios

### Scenario 1: Mobile App Development

```bash
./test_client_brief.sh \
  "Sarah Johnson" \
  "sarah@example.com" \
  "We need a mobile app for iOS and Android that allows users to track their fitness goals. The app should include workout logging, calorie tracking, and social sharing features. Budget is around $50,000 and we need it in 3 months."
```

### Scenario 2: E-commerce Website

```bash
./test_client_brief.sh \
  "Mike Williams" \
  "mike@shop.com" \
  "Looking for a developer to build a Shopify-based e-commerce store for our handmade jewelry business. Need custom theme, payment integration, and inventory management. Timeline is 6-8 weeks, budget $15,000-$25,000."
```

### Scenario 3: Enterprise CRM (Tested Successfully)

```bash
./test_client_brief.sh \
  "Marcus Chen" \
  "marcus.chen@techstartup.io" \
  "We need a comprehensive CRM system for 50+ sales reps across 3 regions. Must include contact management, deal tracking, email integration (Gmail), reporting dashboards, and integrate with Slack and QuickBooks. Budget: $80K-$120K, Timeline: 3-4 months, High urgency."
```

## Expected Results

For each test, you should see:

1. **Ingestion Confirmation**
   - Intake ID
   - Word count
   - Processing status

2. **AI Summary**
   - Professional summary of requirements
   - Completeness assessment
   - Suggested clarifying questions

3. **Structured Data**
   - 15-20 extracted fields
   - Normalized enum values
   - Calculated scores and priorities

4. **Completeness Score**
   - Typically 70-95% for detailed briefs
   - Missing fields identified
   - Critical vs. non-critical gaps

## Troubleshooting

### Server not responding
```bash
# Check if server is running
curl http://localhost:8000/api/v1/health

# Restart server
cd backend
uvicorn client_need_service.main:app --reload --host 0.0.0.0 --port 8000
```

### Database issues
```bash
# Check database connection
psql -h localhost -U aspire_user -d aspire_db -c "SELECT 1;"

# Check tables exist
psql -h localhost -U aspire_user -d aspire_db -c "\dt"
```

### Azure OpenAI not working
Check environment variables in `.env`:
```
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_NAME=...
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Performance Metrics

- **Ingestion**: ~50-200ms (text), ~500-2000ms (PDF/audio)
- **AI Extraction**: ~3-7 seconds (Azure OpenAI processing)
- **Total Processing**: ~5-10 seconds end-to-end
- **Completeness**: Typically 70-95% for detailed briefs
- **Accuracy**: High for explicit information, good inference for implicit details

## Next Steps

1. Test with various client brief formats
2. Test PDF ingestion with project proposal documents
3. Test audio ingestion with recorded client calls
4. Integrate with frontend application
5. Add conversation flow for gathering missing information
6. Implement matching algorithm to pair needs with providers
