# Testing How It Works

Step-by-step guide to run the backend and try **audio file** and **real-time voice streaming** features.

---

## 1. Start the server

From the `backend` folder:

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` from `.env.example` and set at least:

- **Azure Speech** (for transcribe and streaming): `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`
- **Supabase** (for intake/DB): `DATABASE_URL` or `DB_*` if you use intake/agent

Then:

```bash
uvicorn client_need_service.main:app --reload --port 8000
```

Server runs at **http://localhost:8000**.  
API docs: **http://localhost:8000/docs**

---

## 2. Quick health check

```bash
curl http://localhost:8000/api/v1/health
```

You should get something like `{"status":"healthy",...}`.

---

## 3. Test audio file transcription (POST /transcribe)

**Transcribe** turns an uploaded audio file into text (no DB).

You need a real audio file (WAV, MP3, OGG, or M4A). Example with a file on disk:

```bash
curl -X POST http://localhost:8000/api/v1/speech/transcribe \
  -F "audio_file=@/path/to/your/audio.wav"
```

Replace `/path/to/your/audio.wav` with your file. For MP3:

```bash
curl -X POST http://localhost:8000/api/v1/speech/transcribe \
  -F "audio_file=@/path/to/recording.mp3"
```

**Success:** JSON with `transcription`, `confidence`, `duration_seconds`.

**Validation examples:**

- **File too large** (over `MAX_AUDIO_FILE_SIZE_MB` in config):

  ```bash
  # Create a 15 MB file (if your limit is 10 MB)
  dd if=/dev/zero of=/tmp/big.wav bs=1M count=15
  curl -X POST http://localhost:8000/api/v1/speech/transcribe -F "audio_file=@/tmp/big.wav"
  ```

  Expect **413** and `"error_code": "file_too_large"`.

- **Empty file:**
  ```bash
  touch /tmp/empty.wav
  curl -X POST http://localhost:8000/api/v1/speech/transcribe -F "audio_file=@/tmp/empty.wav"
  ```
  Expect **400** and `"error_code": "file_too_small"`.

---

## 4. Test audio upload for intake (POST /upload/audio)

**Intake upload/audio** transcribes the file and creates an intake package (and optionally a client need via the agent).

Same idea as transcribe, but endpoint is different and you can pass client info:

```bash
curl -X POST http://localhost:8000/api/v1/intake/upload/audio \
  -F "file=@/path/to/your/audio.wav" \
  -F "client_name=Test User" \
  -F "client_email=test@example.com"
```

**Success:** JSON with intake package `id`, `status`, etc.

**Validation** (file too large, empty, wrong format) returns the same `error_code` style as transcribe (e.g. **413** `file_too_large`, **400** `file_too_small` or `unsupported_format`).

---

## 5. Test real-time voice streaming (WebSocket)

The **streaming** endpoint accepts a live audio stream and returns interim and final transcripts.

**URL:** `ws://localhost:8000/api/v1/speech/stream`

**Query params (optional):**

- `conversation_id` – link this stream to a conversation for later aggregation
- `language` – e.g. `en-US` (default)

**Protocol:**

- **You send:**
  - **Binary:** raw audio chunks, **16 kHz, 16-bit, mono PCM**.
  - **Text (JSON):** control messages, e.g. `{"type": "stop_session"}`, `{"type": "ping"}`.
- **Server sends (JSON):**
  - `session_started` – with `session_id`
  - `transcript` – interim (`is_final: false`) and final (`is_final: true`)
  - `session_stopped` – when you send `stop_session` or disconnect
  - `error` – on failure

**Ways to try it:**

1. **Browser / custom app**  
   Connect to `ws://localhost:8000/api/v1/speech/stream?language=en-US`.  
   Send binary PCM chunks (16 kHz, 16-bit, mono).  
   Optionally send `{"type": "ping"}` and you should get `{"type": "pong"}`.

2. **wscat (CLI)**  
   Install: `npm install -g wscat`  
   Connect:

   ```bash
   wscat -c "ws://localhost:8000/api/v1/speech/stream?language=en-US"
   ```

   You’ll see `session_started` and any `transcript` / `error` messages.  
   Typing text sends text frames (e.g. `{"type": "ping"}`); for real recognition you must send **binary** PCM (e.g. from a file or mic via another script).

3. **Simple Python WebSocket client**  
   Example that connects, sends a small PCM file, and prints server messages:

   ```python
   import asyncio
   import json
   import wave
   import websockets

   async def test_stream():
       uri = "ws://localhost:8000/api/v1/speech/stream?language=en-US"
       async with websockets.connect(uri) as ws:
           # Session started
           msg = await ws.recv()
           print("Server:", json.loads(msg))

           # Send PCM file (16kHz, 16-bit, mono) if you have one
           # with wave.open("test.wav", "rb") as w:
           #     assert w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == 16000
           #     await ws.send(w.readframes(w.getnframes()))

           # Or just ping
           await ws.send(json.dumps({"type": "ping"}))
           print("Server:", await ws.recv())

           await ws.send(json.dumps({"type": "stop_session"}))

   asyncio.run(test_stream())
   ```

   Install: `pip install websockets`.  
   For real speech, send binary PCM (e.g. from a WAV that is 16 kHz, 16-bit, mono).

---

## 6. Summary

| What you’re testing     | Endpoint / URL                     | How                                                          |
| ----------------------- | ---------------------------------- | ------------------------------------------------------------ |
| Health                  | `GET /api/v1/health`               | `curl http://localhost:8000/api/v1/health`                   |
| Transcribe audio file   | `POST /api/v1/speech/transcribe`   | `curl -X POST ... -F "audio_file=@file.wav"`                 |
| Upload audio for intake | `POST /api/v1/intake/upload/audio` | `curl -X POST ... -F "file=@file.wav" ...`                   |
| Real-time voice stream  | `WS /api/v1/speech/stream`         | WebSocket client; send 16 kHz 16-bit mono PCM + control JSON |
| API docs                | http://localhost:8000/docs         | Open in browser and try from Swagger UI                      |

For **transcribe** and **upload/audio**, errors return a body with `error_code` (e.g. `file_too_large`, `file_too_small`, `unsupported_format`, `no_speech_detected`, `transcription_service_error`) so you can see how validation and Azure errors behave.
