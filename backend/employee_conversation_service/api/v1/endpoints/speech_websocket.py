"""
WebSocket endpoint for real-time speech streaming (employee service).

Protocol:
- Client sends binary audio chunks (16 kHz, 16-bit, mono PCM).
- Server sends JSON transcript events (interim and final).
- Control messages (stop_session, get_session_info, ping) are JSON text frames.
"""

import asyncio
import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    Query,
    HTTPException,
    status,
)

from employee_conversation_service.services.speech_streaming_service import (
    SpeechStreamingService,
    TranscriptEvent,
    get_speech_streaming_service,
)
from employee_conversation_service.core.exceptions import (
    ConversationError,
    SpeechServiceError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["speech-streaming"])


@router.websocket("/stream")
async def speech_stream_websocket(
    websocket: WebSocket,
    conversation_id: Optional[str] = Query(
        None, description="Optional conversation ID for transcript aggregation"
    ),
    language: str = Query(
        "en-US", description="Speech recognition language (e.g. en-US)"
    ),
    speech_service: SpeechStreamingService = Depends(get_speech_streaming_service),
):
    """
    Real-time speech streaming over WebSocket.

    - **Binary frames**: Raw audio (16 kHz, 16-bit, mono PCM). Chunks should be reasonable size (~2 s max per frame).
    - **Text frames**: JSON control messages: `{"type": "stop_session"}`, `{"type": "get_session_info"}`, `{"type": "ping"}`.
    - **Server → Client**: JSON events `session_started`, `transcript`, `session_stopped`, `session_info`, `pong`, `error`.
    """
    await websocket.accept()
    session_id: Optional[str] = None

    try:
        session_id = await speech_service.create_session(
            conversation_id=conversation_id,
            language=language,
        )
        session_info = await speech_service.get_session_info(session_id)

        await websocket.send_text(
            json.dumps(
                {
                    "type": "session_started",
                    "session_id": session_id,
                    "conversation_id": conversation_id,
                    "language": language,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "created_at": session_info.get("created_at"),
                }
            )
        )

        async def on_transcript(event: TranscriptEvent) -> None:
            try:
                payload = {
                    "type": "transcript",
                    **asdict(event),
                }
                await websocket.send_text(json.dumps(payload))
            except Exception as e:
                logger.error("Failed to send transcript: %s", e)

        async def on_error(error: Exception) -> None:
            try:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": str(error),
                            "session_id": session_id,
                        }
                    )
                )
            except Exception as e:
                logger.error("Failed to send error: %s", e)

        await speech_service.start_recognition(
            session_id=session_id,
            transcript_callback=on_transcript,
            error_callback=on_error,
            loop=asyncio.get_running_loop(),
        )

        while True:
            message = await websocket.receive()

            if message.get("type") == "websocket.receive":
                if "bytes" in message:
                    audio_data = message["bytes"]
                    if len(audio_data) > 64000:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "error",
                                    "message": "Audio chunk too large",
                                    "session_id": session_id,
                                }
                            )
                        )
                        continue
                    await speech_service.add_audio_chunk(session_id, audio_data)

                elif "text" in message:
                    try:
                        control = json.loads(message["text"])
                        msg_type = control.get("type")

                        if msg_type == "stop_session":
                            summary = await speech_service.stop_session(session_id)
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "session_stopped",
                                        **summary,
                                    }
                                )
                            )
                            break

                        if msg_type == "get_session_info":
                            info = await speech_service.get_session_info(session_id)
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "session_info",
                                        **info,
                                    }
                                )
                            )

                        elif msg_type == "ping":
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "pong",
                                        "session_id": session_id,
                                    }
                                )
                            )

                        else:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "error",
                                        "message": f"Unknown control type: {msg_type}",
                                        "session_id": session_id,
                                    }
                                )
                            )
                    except json.JSONDecodeError:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "error",
                                    "message": "Invalid JSON in control message",
                                    "session_id": session_id,
                                }
                            )
                        )

            elif message.get("type") == "websocket.disconnect":
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.exception("Speech streaming WebSocket error: %s", e)
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "message": str(e),
                    }
                )
            )
        except Exception:
            pass
    finally:
        if session_id:
            try:
                await speech_service.stop_session(session_id)
                logger.info("Cleaned up session: %s", session_id)
            except ConversationError:
                pass
            except Exception as e:
                logger.error("Error cleaning up session %s: %s", session_id, e)


@router.get("/sessions/{session_id}")
async def get_session_info(
    session_id: str,
    speech_service: SpeechStreamingService = Depends(get_speech_streaming_service),
):
    """
    Get information about a streaming session.

    Returns 404 if the session does not exist or has already been stopped.
    """
    try:
        info = await speech_service.get_session_info(session_id)
        return {"success": True, "data": info}
    except ConversationError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "details": e.details},
        )
    except SpeechServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
