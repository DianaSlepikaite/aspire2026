# ASPIRE 2026 - Client Need Service Agent

AI-powered service agent that conducts natural conversations with clients to extract and understand their project needs. Built with FastAPI, Azure OpenAI, Azure Speech Services, and Supabase.

## Features

- **Conversational AI**: Natural language conversations using Azure OpenAI GPT-4
- **Information Extraction**: Automatic extraction of project requirements, skills, budget, timeline, and urgency
- **Speech Integration**: Speech-to-text and text-to-speech capabilities using Azure Speech SDK
- **Profile Management**: Structured storage of client needs in Supabase PostgreSQL
- **Real-time Progress Tracking**: Monitor conversation completeness and missing information
- **REST API**: Comprehensive API for integration with frontend applications

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       FRONTEND LAYER                            │
│  Next.js/React App                                              │
│  ├─ Employee Agent Interface (Speech + Text)                    │
│  ├─ Client Need Agent Interface (Speech + Text)                 │
│  └─ Match Dashboard (View results)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API LAYER (FastAPI)                       │
│  ├─ /api/v1/conversation/*                                      │
│  ├─ /api/v1/client-needs/*                                      │
│  ├─ /api/v1/speech/*                                            │
│  └─ /api/v1/health                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌──────────────────────┐              ┌──────────────────────────┐
│  CLIENT NEED AGENT   │              │  SERVICES                │
│  SERVICE             │              ├──────────────────────────┤
│ • Conversation Flow  │              │ • Azure OpenAI Service   │
│ • Need Extraction    │              │ • Azure Speech Service   │
│ • Profile Building   │              │ • Storage Service        │
└──────────────────────┘              │ • Extraction Service     │
                                      └──────────────────────────┘
        │
        └─────────────────────┬─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                │
│  Supabase (PostgreSQL + Vector Search)                          │
│  ├─ client_needs                                                │
│  ├─ conversation_messages                                       │
│  └─ extraction_history                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **AI Services**:
  - Azure OpenAI (GPT-4 for conversations)
  - Azure Speech SDK (Speech-to-Text & Text-to-Speech)
- **Database**: Supabase (PostgreSQL)
- **Key Libraries**:
  - openai (Azure OpenAI client)
  - azure-cognitiveservices-speech
  - supabase-py
  - pydantic (data validation)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Azure subscription with:
  - Azure OpenAI Service access
  - Azure Speech Service
- Supabase account and project

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd aspire2026/backend
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Setup Azure Services**

Follow the detailed guide in [docs/AZURE_SETUP.md](docs/AZURE_SETUP.md) to:
- Create Azure OpenAI resource
- Deploy GPT-4 model
- Create Azure Speech Service
- Get API credentials

5. **Setup Supabase**

- Create a Supabase project at [supabase.com](https://supabase.com)
- Run the SQL script from `backend/schema.sql` in the Supabase SQL Editor
- Get your project URL and API keys

6. **Configure environment variables**

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure Speech
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=eastus

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your_anon_key
```

7. **Run the application**

```bash
# Development mode with auto-reload
uvicorn client_need_service.main:app --reload --port 8000

# Or run directly
python -m client_need_service.main
```

8. **Access the API**

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

## API Endpoints

### Conversation Management

- `POST /api/v1/conversation/start` - Start new conversation
- `POST /api/v1/conversation/{id}/message` - Send message
- `GET /api/v1/conversation/{id}/status` - Get conversation status
- `POST /api/v1/conversation/{id}/complete` - Complete conversation
- `GET /api/v1/conversation/{id}/history` - Get message history

### Client Needs CRUD

- `GET /api/v1/client-needs` - List client need profiles
- `GET /api/v1/client-needs/{id}` - Get specific profile
- `PATCH /api/v1/client-needs/{id}` - Update profile
- `DELETE /api/v1/client-needs/{id}` - Delete profile

### Speech Services

- `POST /api/v1/speech/transcribe` - Speech-to-text
- `POST /api/v1/speech/synthesize` - Text-to-speech
- `GET /api/v1/speech/voices` - Get available voices

### Health Checks

- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed service status

## Usage Example

### Starting a Conversation

```bash
curl -X POST http://localhost:8000/api/v1/conversation/start \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Doe",
    "client_email": "john@example.com",
    "source_channel": "web"
  }'
```

### Sending a Message

```bash
curl -X POST http://localhost:8000/api/v1/conversation/{conversation_id}/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a web developer to build an e-commerce platform",
    "message_type": "text"
  }'
```

## Project Structure

```
backend/
├── client_need_service/
│   ├── main.py                      # FastAPI application
│   ├── config.py                    # Configuration
│   ├── api/v1/endpoints/           # API endpoints
│   ├── models/schemas.py           # Pydantic models
│   ├── services/                   # Business logic
│   ├── core/                       # Core utilities
│   └── prompts/                    # AI prompts
├── tests/                          # Test suite
├── requirements.txt
├── .env.example
└── schema.sql                      # Database schema
```

## Development

### Running Tests

```bash
pytest tests/ -v --cov=client_need_service
```

## Documentation

- [Azure Setup Guide](docs/AZURE_SETUP.md) - Complete Azure services setup
- API Documentation - Available at `/docs` when running the server

## License

See the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Employee agent service implementation
- [ ] Matching engine with semantic search
- [ ] Next.js frontend application
- [ ] Real-time updates with WebSockets

## Acknowledgments

Built for ASPIRE 2026 Hackathon - Connecting talent with opportunities through AI-powered conversations.
