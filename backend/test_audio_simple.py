#!/usr/bin/env python3
"""
Simple test for audio transcription service.
Tests with a real audio file provided by the user.
"""

import asyncio
import sys
from pathlib import Path

import httpx


BASE_URL = "http://localhost:8000/api/v1"


async def test_transcribe(audio_file_path: str):
    """Test transcription with a user-provided audio file."""

    print("\n" + "="*60)
    print("Audio Transcription Test")
    print("="*60)

    # Check service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✓ Service is healthy\n")
            else:
                print(f"⚠ Service returned status {response.status_code}\n")
                return
    except Exception as e:
        print(f"✗ Cannot connect to service: {e}\n")
        return

    # Check file exists
    file_path = Path(audio_file_path)
    if not file_path.exists():
        print(f"✗ File not found: {audio_file_path}\n")
        print("Please provide a valid audio file path.")
        print("Supported formats: WAV, MP3, OGG, M4A")
        return

    # Determine content type
    content_types = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
    }
    content_type = content_types.get(file_path.suffix.lower(), "audio/wav")

    print(f"📁 File: {file_path.name}")
    print(f"📊 Size: {file_path.stat().st_size:,} bytes")
    print(f"📋 Format: {file_path.suffix}")
    print(f"\n⏳ Transcribing...")

    # Transcribe
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(audio_file_path, "rb") as f:
                files = {"audio_file": (file_path.name, f, content_type)}
                response = await client.post(
                    f"{BASE_URL}/speech/transcribe",
                    files=files
                )

            if response.status_code == 200:
                data = response.json()
                print(f"\n{'='*60}")
                print("✅ SUCCESS - Transcription Complete")
                print(f"{'='*60}")
                print(f"\n📝 Transcription:")
                print(f"   {data.get('transcription', '')}")
                print(f"\n📊 Confidence: {data.get('confidence', 0):.1%}")
                print(f"⏱  Duration: {data.get('duration_seconds', 0):.2f} seconds")
                print(f"\n{'='*60}\n")
            else:
                print(f"\n{'='*60}")
                print(f"❌ FAILED - Status {response.status_code}")
                print(f"{'='*60}")
                try:
                    error = response.json()
                    detail = error.get('detail', {})
                    if isinstance(detail, dict):
                        print(f"\nError: {detail.get('error', 'Unknown error')}")
                        print(f"Code: {detail.get('error_code', 'N/A')}")
                    else:
                        print(f"\nError: {detail}")
                except:
                    print(f"\n{response.text}")
                print(f"{'='*60}\n")

    except httpx.TimeoutException:
        print(f"\n✗ Request timed out after 30 seconds\n")
    except Exception as e:
        print(f"\n✗ Error: {e}\n")


async def test_websocket():
    """Test WebSocket connection."""
    try:
        import websockets
    except ImportError:
        print("✗ websockets library not installed")
        print("Install with: pip install websockets\n")
        return

    print("\n" + "="*60)
    print("WebSocket Streaming Test")
    print("="*60)

    ws_url = "ws://localhost:8000/api/v1/speech/stream"

    try:
        async with websockets.connect(ws_url) as websocket:
            print("✓ Connected to WebSocket\n")

            # Wait for session_started
            import json
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("type") == "session_started":
                print(f"Session ID: {data.get('session_id')}")
                print(f"Language: {data.get('language')}")

                # Send stop
                await websocket.send(json.dumps({"type": "stop_session"}))
                stop_msg = await websocket.recv()
                stop_data = json.loads(stop_msg)

                if stop_data.get("type") == "session_stopped":
                    print("\n✅ WebSocket streaming endpoint is working!")
                    print(f"{'='*60}\n")

    except Exception as e:
        print(f"✗ WebSocket error: {e}\n")


async def main():
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("Audio-to-Text Testing Script")
        print("="*60)
        print("\nUsage:")
        print("  python test_audio_simple.py <audio_file>")
        print("  python test_audio_simple.py --test-websocket")
        print("\nExamples:")
        print("  python test_audio_simple.py recording.wav")
        print("  python test_audio_simple.py myaudio.mp3")
        print("  python test_audio_simple.py --test-websocket")
        print("\nSupported formats: WAV, MP3, OGG, M4A")
        print("="*60)

        print("\n💡 How to create a test audio file:")
        print("   1. Use your phone/computer to record a short message")
        print("   2. Say something clear like 'Hello, this is a test'")
        print("   3. Save as WAV or MP3 format")
        print("   4. Run this script with that file\n")
        return

    arg = sys.argv[1]

    if arg == "--test-websocket":
        await test_websocket()
    else:
        await test_transcribe(arg)


if __name__ == "__main__":
    asyncio.run(main())
