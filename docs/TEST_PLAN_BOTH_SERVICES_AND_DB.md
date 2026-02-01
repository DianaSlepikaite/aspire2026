# Test Plan: Both Services and DB Tally

Stepwise plan to test **client_need_service** (port 8000) and **employee_conversation_service** (port 8001), then verify database values match API responses.

---

## Prerequisites

- [ ] **Databases**
  - **client_needs_db**: tables `client_needs`, `conversation_messages`, `extraction_history`, `intake_packages`
  - **employee_conversation_db** (or employee_service_db): tables `employee_documents`, `employee_profiles`
- [ ] **.env** (in `backend/`)
  - Client DB: `DATABASE_URL` or `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` → client_needs_db
  - Employee DB: `EMPLOYEE_DATABASE_URL` or `EMPLOYEE_DB_NAME` (and host/user/pass) → employee DB
- [ ] **Services running**
  - Client: `http://localhost:8000`
  - Employee: `http://localhost:8001`
  - e.g. `./START_BOTH_SERVICES.sh` from repo root

---

## Phase 1: Health and DB Connectivity

### 1.1 Client Need Service health

| Step | Action                                             | Expected                                                                                     |
| ---- | -------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 1    | `GET http://localhost:8000/api/v1/health`          | `{"status":"healthy",...}`                                                                   |
| 2    | `GET http://localhost:8000/api/v1/health/detailed` | `status: "healthy"` or `"degraded"`; `services` includes `database` with `status: "healthy"` |

### 1.2 Employee Conversation Service health

| Step | Action                                             | Expected                                                             |
| ---- | -------------------------------------------------- | -------------------------------------------------------------------- |
| 3    | `GET http://localhost:8001/api/v1/health`          | `{"status":"healthy","service":"Employee Conversation Service",...}` |
| 4    | `GET http://localhost:8001/api/v1/health/detailed` | `database` in `services` with `status: "healthy"`                    |

**Tally:** If either detailed health shows `database: unhealthy`, fix DB connection before continuing.

---

## Phase 2: Client Need Service – API and DB

### 2.1 Start a conversation (writes to client_needs + conversation_messages)

| Step | Action                                                                                                                                                   | Expected                                                                |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 5    | `POST http://localhost:8000/api/v1/conversation/start`<br>Body: `{"client_name":"Test Client","client_email":"test@example.com","source_channel":"web"}` | `201`; response has `conversation_id`, `message`, `conversation_status` |
| 6    | Note **conversation_id** (UUID) from response                                                                                                            | e.g. `conv_uuid` for next steps                                         |

### 2.2 Send messages (updates client_needs, inserts conversation_messages)

| Step | Action                                                                                                                                                                                          | Expected                                                               |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 7    | `POST http://localhost:8000/api/v1/conversation/{conversation_id}/message`<br>Body: `{"message":"We need a web developer for an e-commerce project. Budget around 50k.","message_type":"text"}` | `200`; `response` and possibly updated `client_need` / extraction info |
| 8    | (Optional) Send 1–2 more messages to fill project/timeline                                                                                                                                      | `200` each                                                             |

### 2.3 Complete conversation (updates client_needs)

| Step | Action                                                                      | Expected                                  |
| ---- | --------------------------------------------------------------------------- | ----------------------------------------- |
| 9    | `POST http://localhost:8000/api/v1/conversation/{conversation_id}/complete` | `200`; `conversation_status: "completed"` |

### 2.4 List and get client needs (read from DB)

| Step | Action                                                                      | Expected                                                            |
| ---- | --------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| 10   | `GET http://localhost:8000/api/v1/client-needs?limit=10`                    | `200`; `items` array; at least one item with your `conversation_id` |
| 11   | From list response, note **client need `id`** (row id, not conversation_id) | e.g. `client_need_id`                                               |
| 12   | `GET http://localhost:8000/api/v1/client-needs/{client_need_id}`            | `200`; full profile; `conversation_id` matches step 6               |

### 2.5 Intake flow (writes to intake_packages; optional link to client_needs)

| Step | Action                                                                                                                                                                                                              | Expected                                              |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 13   | `POST http://localhost:8000/api/v1/intake/text`<br>Body: `{"text":"Need 2 senior devs, 6 months, remote.","client_name":"Intake Test","client_email":"intake@example.com"}` (or use `/upload/pdf` with a small PDF) | `201`; response has `id` (intake_package id)          |
| 14   | Note **intake_package id**                                                                                                                                                                                          | e.g. for agent or DB check                            |
| 15   | (Optional) `POST http://localhost:8000/api/v1/agent/process-intake`<br>Body: `{"intake_id":"<intake_package_id>"}`                                                                                                  | `200`; agent output; may create/update `client_needs` |

### 2.6 DB tally – client_needs_db

Run in **client_needs_db** (psql or pgAdmin):

```sql
-- Counts
SELECT 'client_needs' AS tbl, COUNT(*) FROM client_needs
UNION ALL SELECT 'conversation_messages', COUNT(*) FROM conversation_messages
UNION ALL SELECT 'extraction_history', COUNT(*) FROM extraction_history
UNION ALL SELECT 'intake_packages', COUNT(*) FROM intake_packages;
```

| Step | Check                         | Expected                                              |
| ---- | ----------------------------- | ----------------------------------------------------- |
| 16   | `client_needs` count          | ≥ 1 (from conversation start + optional intake/agent) |
| 17   | `conversation_messages` count | ≥ 1 per conversation (user + assistant messages)      |
| 18   | `intake_packages` count       | ≥ 1 if you did step 13                                |

**Row-level tally (use your IDs from steps 6 and 11):**

```sql
-- Replace <conversation_id> with the UUID from step 6
SELECT id, conversation_id, client_name, conversation_status, total_messages
FROM client_needs WHERE conversation_id = '<conversation_id>';
```

```sql
SELECT id, conversation_id, role, LEFT(content, 80) AS content_preview
FROM conversation_messages WHERE conversation_id = '<conversation_id>'
ORDER BY created_at;
```

| Step | Check                        | Expected                                                            |
| ---- | ---------------------------- | ------------------------------------------------------------------- |
| 19   | `client_needs` row           | Same `client_name`, `conversation_status`, and message count as API |
| 20   | `conversation_messages` rows | Same number and roles as in conversation history API                |

**Conversation history API vs DB:**

| Step | Action                                                                                  | Expected         |
| ---- | --------------------------------------------------------------------------------------- | ---------------- |
| 21   | `GET http://localhost:8000/api/v1/conversation/{conversation_id}/history`               | List of messages |
| 22   | Compare message count and last message content with `conversation_messages` query above | Match            |

---

## Phase 3: Employee Conversation Service – API and DB

### 3.1 Process upload (writes to employee_documents + employee_profiles)

| Step | Action                                                                                                      | Expected                                                              |
| ---- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 23   | `POST http://localhost:8001/api/v1/agent/process-upload`<br>Form: `file` = a small PDF (e.g. 1-page resume) | `200`; response has `document_id`, `employee_profile_id` (or similar) |
| 24   | Note **document_id** and **employee_profile_id** from response                                              | For DB tally and optional step 25                                     |

### 3.2 (Optional) Process existing document / clarifying questions

| Step | Action                                                                                                                    | Expected                 |
| ---- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| 25   | `POST http://localhost:8001/api/v1/agent/process-document`<br>Body: `{"document_id":"<document_id>"}`                     | `200`                    |
| 26   | `POST http://localhost:8001/api/v1/agent/clarifying-questions`<br>Body: `{"employee_profile_id":"<employee_profile_id>"}` | `200`; list of questions |

### 3.3 DB tally – employee_conversation_db (or employee_service_db)

Run in **employee DB**:

```sql
SELECT 'employee_documents' AS tbl, COUNT(*) FROM employee_documents
UNION ALL SELECT 'employee_profiles', COUNT(*) FROM employee_profiles;
```

| Step | Check                      | Expected                  |
| ---- | -------------------------- | ------------------------- |
| 27   | `employee_documents` count | ≥ 1 (from process-upload) |
| 28   | `employee_profiles` count  | ≥ 1 (from process-upload) |

**Row-level tally (use IDs from step 24):**

```sql
-- Replace <document_id> and <profile_id> with UUIDs from step 24
SELECT id, file_name, status, created_at FROM employee_documents WHERE id = '<document_id>';
SELECT id, created_at, updated_at FROM employee_profiles WHERE id = '<profile_id>';
```

| Step | Check                    | Expected                                                         |
| ---- | ------------------------ | ---------------------------------------------------------------- |
| 29   | `employee_documents` row | Same `id` as API `document_id`; `status` and metadata consistent |
| 30   | `employee_profiles` row  | Same `id` as API `employee_profile_id`                           |

---

## Phase 4: Cross-check summary

| #   | What                                   | Where to check                                       | Pass criteria                                                          |
| --- | -------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------- |
| 31  | Client service uses only client DB     | `.env` + client health/detailed                      | DB in detailed health = healthy; no employee tables in client_needs_db |
| 32  | Employee service uses only employee DB | `.env` + employee health/detailed                    | DB in detailed health = healthy; employee tables only in employee DB   |
| 33  | Client conversation flow               | API responses + client_needs + conversation_messages | One client_needs row per conversation; messages match history API      |
| 34  | Client intake flow                     | intake_packages + optional client_needs              | Intake row exists; optional client_need link correct                   |
| 35  | Employee upload flow                   | employee_documents + employee_profiles               | One document and one profile (or more) per upload; IDs match API       |

---

## Quick reference – Base URLs and DBs

| Service               | Base URL                | Database                 | Tables                                                                   |
| --------------------- | ----------------------- | ------------------------ | ------------------------------------------------------------------------ |
| Client Need           | `http://localhost:8000` | client_needs_db          | client_needs, conversation_messages, extraction_history, intake_packages |
| Employee Conversation | `http://localhost:8001` | employee_conversation_db | employee_documents, employee_profiles                                    |

---

## Optional: Scripted checks

- **Health:**  
  `curl -s http://localhost:8000/api/v1/health/detailed | jq .`  
  `curl -s http://localhost:8001/api/v1/health/detailed | jq .`
- **Client list:**  
  `curl -s "http://localhost:8000/api/v1/client-needs?limit=5" | jq .`
- **DB counts (client_needs_db):**  
  Run the Phase 2.6 SQL in psql/pgAdmin.
- **DB counts (employee DB):**  
  Run the Phase 3.3 SQL in psql/pgAdmin.

Use this plan in order (Phase 1 → 2 → 3 → 4) to test both services and tally API results with database values.
