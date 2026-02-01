# Seeing the Agent Section in Swagger (Employee Service)

The **agent** section (process-upload, process-document, generate-resume, clarifying-questions) exists only on the **Employee Conversation Service** on **port 8001**.

## 1. Confirm you're on the Employee service

- **Employee service (has agent section):** http://localhost:8001/docs
- **Client service (different agent endpoints):** http://localhost:8000/docs

Open **http://localhost:8001** (no `/docs`). You should see something like:

```json
{
  "service": "Employee Conversation Service",
  "agent_base": "/api/v1/agent",
  "agent_endpoints": [
    "POST /api/v1/agent/process-upload",
    "POST /api/v1/agent/process-document",
    ...
  ]
}
```

If you see **"Employee Conversation Service"** and **"agent_endpoints"**, you're on the right service. Then open **http://localhost:8001/docs** for Swagger.

## 2. Restart the Employee service so the latest code is loaded

If you still don't see the agent section:

1. Stop all services:
   ```bash
   pkill -f 'uvicorn.*main:app'
   ```
2. Wait a few seconds, then free the ports:
   ```bash
   lsof -ti:8001 | xargs kill -9   # if needed
   sleep 3
   ```
3. Start again from the **repo root**:
   ```bash
   ./START_BOTH_SERVICES.sh
   ```
4. Open **http://localhost:8001/docs** (not 8000).

## 3. In Swagger UI

- The page title should be **"Employee Conversation Service"**.
- You should see an **"agent"** section (with description: "Employee Service Agent: process-upload, ...").
- Under it: **POST /api/v1/agent/process-upload**, **POST /api/v1/agent/process-document**, **GET /api/v1/agent/generate-resume/...**, **POST /api/v1/agent/clarifying-questions**.

If the title is "Client Need Service" or the URL is port **8000**, you're on the client service; switch to **http://localhost:8001/docs**.
