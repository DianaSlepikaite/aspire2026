# ASPIRE2026 Application Architecture

## System Overview

ASPIRE2026 is an AI-powered talent matching platform that connects employees with client opportunities through conversational interfaces. The system uses microservices architecture with separate services for employee and client management, integrated with Azure AI services.

---

## High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        UI[React Frontend<br/>Vite + TypeScript<br/>ShadCN UI]
    end

    subgraph "Application Layer - Microservices"
        subgraph "Client Need Service<br/>Port 8000"
            CNS_API[FastAPI REST API]
            CNS_WS[WebSocket<br/>Speech Streaming]
            CNS_CONV[Conversation<br/>Service]
            CNS_AGENT[Client Need<br/>Agent]
            CNS_EXTRACT[Need Extraction<br/>Service]
            CNS_MATCH[Matching Agent<br/>AI-Powered]
            CNS_SPEECH[Speech Service<br/>Azure TTS/STT]
            CNS_STORAGE[Storage Service]
        end

        subgraph "Employee Service<br/>Port 8001"
            EMP_API[FastAPI REST API]
            EMP_WS[WebSocket<br/>Speech Streaming]
            EMP_CONV[Conversation<br/>Service]
            EMP_EXTRACT[Skill Extraction<br/>Service]
            EMP_SPEECH[Speech Service<br/>Azure TTS/STT]
            EMP_RESUME[Resume<br/>Generator]
            EMP_STORAGE[Storage Service]
        end
    end

    subgraph "Data Layer"
        CLIENT_DB[(PostgreSQL<br/>client_need_db)]
        EMP_DB[(PostgreSQL<br/>employee_conversation_db)]
    end

    subgraph "External Services - Azure"
        AZURE_OPENAI[Azure OpenAI<br/>GPT-4o]
        AZURE_SPEECH[Azure Speech<br/>TTS/STT]
    end

    UI -->|HTTP/REST| CNS_API
    UI -->|HTTP/REST| EMP_API
    UI -->|WebSocket| CNS_WS
    UI -->|WebSocket| EMP_WS

    CNS_API --> CNS_CONV
    CNS_API --> CNS_AGENT
    CNS_API --> CNS_MATCH
    CNS_CONV --> CNS_EXTRACT
    CNS_CONV --> CNS_SPEECH
    CNS_AGENT --> CNS_EXTRACT
    CNS_CONV --> CNS_STORAGE
    CNS_AGENT --> CNS_STORAGE
    CNS_MATCH --> CNS_STORAGE
    CNS_STORAGE --> CLIENT_DB

    CNS_EXTRACT --> AZURE_OPENAI
    CNS_MATCH --> AZURE_OPENAI
    CNS_SPEECH --> AZURE_SPEECH
    CNS_AGENT --> AZURE_OPENAI

    EMP_API --> EMP_CONV
    EMP_CONV --> EMP_EXTRACT
    EMP_CONV --> EMP_SPEECH
    EMP_CONV --> EMP_STORAGE
    EMP_EXTRACT --> EMP_RESUME
    EMP_STORAGE --> EMP_DB

    EMP_EXTRACT --> AZURE_OPENAI
    EMP_SPEECH --> AZURE_SPEECH

    CNS_MATCH -->|Cross-DB Query| EMP_DB

    style UI fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style CNS_API fill:#7CB342,stroke:#558B2F,color:#fff
    style EMP_API fill:#7CB342,stroke:#558B2F,color:#fff
    style CNS_MATCH fill:#FFA726,stroke:#F57C00,color:#fff
    style AZURE_OPENAI fill:#00BCD4,stroke:#0097A7,color:#fff
    style AZURE_SPEECH fill:#00BCD4,stroke:#0097A7,color:#fff
    style CLIENT_DB fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style EMP_DB fill:#9C27B0,stroke:#6A1B9A,color:#fff
```

---

## Detailed Component Architecture

```mermaid
graph LR
    subgraph "Frontend Application"
        PAGES[Pages Layer]
        COMPONENTS[Components Layer]
        HOOKS[React Hooks]
        API_CLIENT[API Client<br/>clientNeedApi.ts]
        STATE[TanStack Query<br/>State Management]

        PAGES --> COMPONENTS
        PAGES --> HOOKS
        HOOKS --> API_CLIENT
        API_CLIENT --> STATE
    end

    subgraph "Backend Services"
        REST_API[REST API Layer<br/>FastAPI Routers]
        SERVICE_LAYER[Service Layer]
        AGENT_LAYER[AI Agent Layer]
        DATA_LAYER[Data Access Layer]

        REST_API --> SERVICE_LAYER
        SERVICE_LAYER --> AGENT_LAYER
        SERVICE_LAYER --> DATA_LAYER
    end

    API_CLIENT -->|HTTP/JSON| REST_API

    style PAGES fill:#E3F2FD
    style API_CLIENT fill:#B2DFDB
    style REST_API fill:#C8E6C9
    style AGENT_LAYER fill:#FFE0B2
```

---

## Key Features by Service

### Client Need Service (Port 8000)

**API Endpoints:**
- `/api/v1/health` - Health check
- `/api/v1/conversation/*` - Conversation management
- `/api/v1/client-needs/*` - Client need CRUD operations
- `/api/v1/intake/*` - Document/audio intake (PDF, audio, text)
- `/api/v1/matching/*` - AI-powered candidate matching
- `/api/v1/speech/*` - Speech synthesis and recognition
- `/api/v1/agent/*` - AI agent processing

**Core Services:**
1. **Conversation Service** - Manages conversational interactions with clients
2. **Need Extraction Service** - Extracts structured requirements using AI
3. **Matching Agent** - AI-powered employee-to-client need matching
4. **Speech Service** - Azure TTS/STT integration
5. **Client Need Agent** - Orchestrates requirement gathering workflow
6. **Storage Service** - Database operations for client needs

**Key Capabilities:**
- Conversational requirement gathering (text + voice)
- Multi-format intake (PDF, audio, text)
- AI-powered requirement extraction
- Intelligent candidate matching with explanations
- Real-time completeness tracking
- Speech-to-text and text-to-speech

### Employee Conversation Service (Port 8001)

**API Endpoints:**
- `/api/v1/health` - Health check
- `/api/v1/conversation/*` - Conversation management
- `/api/v1/employee-profiles/*` - Employee profile operations
- `/api/v1/speech/*` - Speech synthesis and recognition
- `/api/v1/agent/*` - AI agent interactions

**Core Services:**
1. **Conversation Service** - Manages employee conversations
2. **Skill Extraction Service** - AI-powered profile extraction
3. **Speech Service** - Azure TTS/STT integration
4. **Resume Generator** - PDF CV generation
5. **Storage Service** - Database operations for employee profiles

**Key Capabilities:**
- Conversational profile building (text + voice)
- Real-time skill/experience extraction
- AI-enhanced CV generation
- Profile completeness scoring
- Dynamic resume updates

---

## Data Models

### Client Need Entity

```
client_needs
├── id (UUID)
├── client_name
├── client_company
├── client_email
├── project_title
├── project_description
├── required_skills (JSONB Array)
├── skill_level
├── certifications_required (JSONB Array)
├── required_roles (JSONB Array with categories)
├── timeline_duration_weeks
├── timeline_start_date
├── work_location
├── budget_min/max/type
├── urgency_level
├── profile_completeness_score
├── missing_information (JSONB Array)
├── conversation_status
└── timestamps
```

### Employee Profile Entity

```
employee_profiles
├── id (UUID)
├── full_name
├── email
├── phone
├── summary
├── experience_years
├── skills (JSONB Array)
├── certifications (JSONB Array)
├── education (JSONB Array)
├── experience (JSONB Array)
├── preferred_roles (JSONB Array)
├── profile_completeness_score
└── timestamps
```

### Match Result Entity

```
CandidateMatch
├── employee_profile_id
├── employee_name
├── match_score (0-100)
├── confidence (0.0-1.0)
├── rank (1-N)
├── explanation
│   ├── strengths (Array)
│   ├── gaps (Array)
│   ├── skill_matches (Array)
│   └── additional_notes
├── experience_years
├── key_skills
└── current_availability
```

---

## Technology Stack

### Frontend
- **Framework**: React 18.3
- **Build Tool**: Vite 5.4
- **Language**: TypeScript 5.8
- **UI Library**: ShadCN UI (Radix UI primitives)
- **Styling**: Tailwind CSS 3.4
- **State Management**: TanStack Query (React Query) 5.83
- **Routing**: React Router 6.30
- **Form Handling**: React Hook Form 7.61 + Zod 3.25
- **Charts**: Recharts 2.15

### Backend
- **Framework**: FastAPI (Python)
- **Language**: Python 3.14
- **Database**: PostgreSQL with asyncpg
- **ORM**: SQLAlchemy (async)
- **Validation**: Pydantic v2
- **AI Framework**: LangChain
- **Testing**: pytest, httpx

### External Services
- **AI**: Azure OpenAI (GPT-4o deployment)
- **Speech**: Azure Speech Services (TTS/STT)
- **PDF Generation**: ReportLab

### Infrastructure
- **API Gateway**: None (direct service access)
- **Authentication**: Not implemented yet
- **Deployment**: Local development
- **Monitoring**: FastAPI built-in logging

---

## API Communication Flow

### Example: Client Need Matching Flow

```mermaid
sequenceDiagram
    participant UI as Frontend UI
    participant CNS as Client Need Service
    participant EMP_DB as Employee DB
    participant AOAI as Azure OpenAI

    UI->>CNS: POST /api/v1/matching/find-candidates
    Note over UI,CNS: { client_need_id, max_results, min_score }

    CNS->>CNS: Get client need details
    CNS->>EMP_DB: Query employee profiles
    Note over CNS,EMP_DB: Cross-database query

    EMP_DB-->>CNS: Return employee profiles

    loop For each candidate
        CNS->>CNS: Pre-filter by skills
        CNS->>AOAI: Evaluate match with prompt
        Note over CNS,AOAI: Includes client requirements<br/>and candidate profile
        AOAI-->>CNS: Match score + explanation
        CNS->>CNS: Build CandidateMatch object
    end

    CNS->>CNS: Sort by score, assign ranks
    CNS-->>UI: Return ranked matches
    Note over UI,CNS: MatchResponse with detailed<br/>explanations and scores
```

### Example: Employee Profile Building Flow

```mermaid
sequenceDiagram
    participant UI as Frontend UI
    participant EMP as Employee Service
    participant AOAI as Azure OpenAI
    participant DB as Employee DB

    UI->>EMP: POST /api/v1/conversation/start
    EMP->>DB: Create employee profile
    EMP->>AOAI: Generate greeting
    EMP-->>UI: conversation_id, greeting

    UI->>EMP: POST /api/v1/conversation/{id}/message
    Note over UI,EMP: User shares experience

    EMP->>AOAI: Process conversation
    AOAI-->>EMP: Extract skills/experience

    EMP->>DB: Update employee profile
    EMP->>EMP: Calculate completeness

    EMP-->>UI: Response + extraction updates
    Note over UI,EMP: Real-time profile updates
```

---

## Security Considerations

### Current State
- ⚠️ No authentication/authorization implemented
- ⚠️ Direct database access (no connection pooling limits)
- ⚠️ No rate limiting
- ⚠️ CORS not configured for production
- ⚠️ API keys stored in environment variables

### Recommended Improvements
1. Implement OAuth2/JWT authentication
2. Add API key management system
3. Enable CORS with whitelist
4. Add rate limiting per client
5. Implement request validation middleware
6. Use Azure Key Vault for secrets
7. Add audit logging for sensitive operations
8. Implement role-based access control (RBAC)

---

## Scalability Considerations

### Current Limitations
- Single instance per service
- No load balancing
- Synchronous AI calls (blocking)
- No caching layer
- Direct database connections

### Scaling Strategy
1. **Horizontal Scaling**
   - Containerize services (Docker)
   - Deploy on Kubernetes/AKS
   - Add load balancer (Azure Load Balancer)

2. **Database Optimization**
   - Connection pooling (asyncpg pools)
   - Read replicas for queries
   - Partition large tables
   - Add caching layer (Redis)

3. **AI Service Optimization**
   - Implement request batching
   - Add response caching
   - Use Azure API Management
   - Implement circuit breakers

4. **Frontend Optimization**
   - CDN for static assets
   - Code splitting
   - Service worker for offline support
   - WebSocket connection pooling

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer<br/>Azure Front Door]

        subgraph "Frontend"
            FE1[Static Site<br/>Azure Static Web Apps]
        end

        subgraph "Backend - Client Service"
            CNS1[Client Need Service<br/>Container Instance 1]
            CNS2[Client Need Service<br/>Container Instance 2]
        end

        subgraph "Backend - Employee Service"
            EMP1[Employee Service<br/>Container Instance 1]
            EMP2[Employee Service<br/>Container Instance 2]
        end

        subgraph "Data"
            DB_PRIMARY[(PostgreSQL Primary)]
            DB_REPLICA[(PostgreSQL Read Replica)]
            REDIS[(Redis Cache)]
        end

        subgraph "Azure Services"
            AZURE_AI[Azure OpenAI]
            AZURE_SPEECH_SVC[Azure Speech]
            KEY_VAULT[Azure Key Vault]
        end
    end

    LB --> FE1
    LB --> CNS1
    LB --> CNS2
    LB --> EMP1
    LB --> EMP2

    CNS1 --> DB_PRIMARY
    CNS2 --> DB_PRIMARY
    CNS1 --> DB_REPLICA
    CNS2 --> DB_REPLICA
    CNS1 --> REDIS
    CNS2 --> REDIS

    EMP1 --> DB_PRIMARY
    EMP2 --> DB_PRIMARY
    EMP1 --> DB_REPLICA
    EMP2 --> DB_REPLICA
    EMP1 --> REDIS
    EMP2 --> REDIS

    CNS1 --> AZURE_AI
    CNS2 --> AZURE_AI
    EMP1 --> AZURE_AI
    EMP2 --> AZURE_AI

    CNS1 --> AZURE_SPEECH_SVC
    CNS2 --> AZURE_SPEECH_SVC
    EMP1 --> AZURE_SPEECH_SVC
    EMP2 --> AZURE_SPEECH_SVC

    CNS1 --> KEY_VAULT
    CNS2 --> KEY_VAULT
    EMP1 --> KEY_VAULT
    EMP2 --> KEY_VAULT

    style LB fill:#FF6B6B
    style FE1 fill:#4A90E2
    style REDIS fill:#DC143C,color:#fff
    style KEY_VAULT fill:#FFD700
```

---

## Monitoring and Observability

### Recommended Tools
1. **Application Monitoring**: Azure Application Insights
2. **Log Aggregation**: Azure Log Analytics
3. **Metrics**: Prometheus + Grafana
4. **Tracing**: OpenTelemetry
5. **Alerting**: Azure Monitor Alerts

### Key Metrics to Track
- API response times (p50, p95, p99)
- Error rates by endpoint
- AI service latency
- Database query performance
- WebSocket connection count
- Match quality scores
- Profile completeness distribution

---

## Development Workflow

```mermaid
graph LR
    DEV[Local Development] --> TEST[Testing]
    TEST --> BUILD[Build & Package]
    BUILD --> STAGING[Staging Environment]
    STAGING --> PROD[Production]

    TEST -.->|Failed| DEV
    STAGING -.->|Failed| BUILD

    style DEV fill:#E3F2FD
    style TEST fill:#FFF9C4
    style BUILD fill:#C8E6C9
    style STAGING fill:#FFE0B2
    style PROD fill:#FFCDD2
```

### Local Development Setup
1. Clone repository
2. Setup Python virtual environment
3. Install dependencies (`pip install -r requirements.txt`)
4. Configure Azure credentials (`.env` files)
5. Setup PostgreSQL databases
6. Run migrations
7. Start services (`uvicorn` for backend, `npm run dev` for frontend)

### Testing Strategy
- **Unit Tests**: pytest for Python, Vitest for TypeScript
- **Integration Tests**: Test API endpoints with httpx
- **E2E Tests**: Playwright (recommended)
- **AI Tests**: Mock Azure OpenAI responses

---

## API Documentation

Each service provides interactive API documentation:
- **Client Need Service**: http://localhost:8000/docs
- **Employee Service**: http://localhost:8001/docs

Documentation is auto-generated by FastAPI using OpenAPI 3.0 specification.

---

## Future Enhancements

### Planned Features
1. **Authentication & Authorization**
   - User registration/login
   - Role-based access (admin, recruiter, employee)
   - OAuth2 integration

2. **Real-Time Features**
   - Live match notifications
   - Chat between recruiters and candidates
   - Real-time profile updates

3. **Analytics Dashboard**
   - Match success metrics
   - Pipeline analytics
   - AI performance monitoring

4. **Advanced Matching**
   - Cultural fit analysis
   - Salary negotiation assistant
   - Team composition recommendations

5. **Integration Capabilities**
   - ATS integration (Greenhouse, Lever)
   - Calendar integration (scheduling)
   - Email notifications
   - Slack/Teams bot integration

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure Speech Service](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/)
- [React Documentation](https://react.dev/)
- [TanStack Query](https://tanstack.com/query/latest)
- [ShadCN UI](https://ui.shadcn.com/)

---

**Document Version**: 1.0
**Last Updated**: February 1, 2026
**Maintained By**: ASPIRE2026 Development Team
