#!/usr/bin/env python3
"""
Test script for audio-to-text functionality.
Tests both file upload transcription and real-time WebSocket streaming.

Usage:
    # Test with a sample audio file
    python test_audio_transcription.py --file path/to/audio.wav

    # Generate and test with a sample audio file
    python test_audio_transcription.py --generate-sample

    # Test WebSocket streaming (requires separate audio recording)
    python test_audio_transcription.py --test-websocket
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import httpx


BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0


def generate_sample_audio(output_path: str = "test_sample.wav") -> str:
    """
    Generate a sample WAV audio file for testing using text-to-speech.
    Returns the path to the generated file.
    """
    try:
        import numpy as np
        from scipy.io import wavfile
    except ImportError:
        print("Error: numpy and scipy are required to generate sample audio.")
        print("Install with: pip install numpy scipy")
        sys.exit(1)

    # Generate a simple sine wave (beep sound) at 440 Hz for 2 seconds
    sample_rate = 16000  # 16 kHz
    duration = 2.0  # seconds
    frequency = 440.0  # A4 note in Hz

    t = np.linspace(0, duration, int(sample_rate * duration))
    # Create a sine wave with fade in/out to avoid clicks
    audio_data = np.sin(2 * np.pi * frequency * t)

    # Add fade in/out
    fade_samples = int(sample_rate * 0.1)  # 100ms fade
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    audio_data[:fade_samples] *= fade_in
    audio_data[-fade_samples:] *= fade_out

    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)

    wavfile.write(output_path, sample_rate, audio_data)
    print(f"✓ Generated sample audio file: {output_path}")
    return output_path


async def check_service_health() -> bool:
    """Check if the service is running and healthy."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✓ Service is running and healthy")
                return True
            else:
                print(f"⚠ Service returned status {response.status_code}")
                return False
    except httpx.ConnectError:
        print("✗ Cannot connect to service. Is it running on http://localhost:8000?")
        print("\nTo start the service, run:")
        print("  cd backend")
        print("  uvicorn client_need_service.main:app --reload")
        return False
    except Exception as e:
        print(f"✗ Error checking service health: {e}")
        return False


async def test_transcribe_file(audio_file_path: str) -> None:
    """Test the file upload transcription endpoint."""
    print(f"\n{'='*60}")
    print("Testing File Upload Transcription")
    print(f"{'='*60}")

    file_path = Path(audio_file_path)

    if not file_path.exists():
        print(f"✗ File not found: {audio_file_path}")
        return

    # Determine content type from extension
    content_types = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
    }
    content_type = content_types.get(file_path.suffix.lower(), "audio/wav")

    print(f"📁 File: {audio_file_path}")
    print(f"📊 Size: {file_path.stat().st_size} bytes")
    print(f"📋 Content-Type: {content_type}")
    print(f"\n⏳ Uploading and transcribing...")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            with open(audio_file_path, "rb") as f:
                files = {"audio_file": (file_path.name, f, content_type)}
                response = await client.post(
                    f"{BASE_URL}/speech/transcribe",
                    files=files
                )

            print(f"\n📤 Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ Transcription successful!")
                print(f"\n{'─'*60}")
                print(f"📝 Transcription: {data.get('transcription', '')}")
                print(f"📊 Confidence: {data.get('confidence', 0):.2%}")
                print(f"⏱  Duration: {data.get('duration_seconds', 0):.2f} seconds")
                print(f"{'─'*60}")
            else:
                print(f"\n✗ Transcription failed!")
                try:
                    error_data = response.json()
                    print(f"Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Response: {response.text}")

    except httpx.TimeoutException:
        print(f"✗ Request timed out after {TIMEOUT} seconds")
    except Exception as e:
        print(f"✗ Error: {e}")


async def test_websocket_streaming() -> None:
    """Test the WebSocket streaming endpoint."""
    print(f"\n{'='*60}")
    print("Testing WebSocket Streaming")
    print(f"{'='*60}")

    try:
        import websockets
    except ImportError:
        print("✗ websockets library required for streaming test")
        print("Install with: pip install websockets")
        return

    print("\n⚠ WebSocket streaming requires real-time audio input.")
    print("This is a basic connection test.")

    ws_url = "ws://localhost:8000/api/v1/speech/stream"

    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✓ Connected to {ws_url}")

            # Wait for session_started message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"\n📨 Received: {data.get('type', 'unknown')}")

            if data.get("type") == "session_started":
                session_id = data.get("session_id")
                print(f"   Session ID: {session_id}")
                print(f"   Language: {data.get('language')}")

                # Send a ping
                await websocket.send(json.dumps({"type": "ping"}))
                print("\n⏳ Sent ping...")

                pong = await websocket.recv()
                pong_data = json.loads(pong)
                if pong_data.get("type") == "pong":
                    print("✓ Received pong")

                # Stop the session
                await websocket.send(json.dumps({"type": "stop_session"}))
                print("⏳ Stopping session...")

                stop_msg = await websocket.recv()
                stop_data = json.loads(stop_msg)
                if stop_data.get("type") == "session_stopped":
                    print("✓ Session stopped successfully")
                    print(f"\n📊 Session Summary:")
                    print(f"   Duration: {stop_data.get('duration_seconds', 0):.2f}s")
                    print(f"   Transcripts: {stop_data.get('transcript_count', 0)}")

    except ImportError:
        print("✗ websockets library not installed")
        print("Install with: pip install websockets")
    except Exception as e:
        print(f"✗ WebSocket error: {e}")


async def main():
    parser = argparse.ArgumentParser(
        description="Test audio-to-text functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to audio file to transcribe (WAV, MP3, OGG, M4A)"
    )
    parser.add_argument(
        "--generate-sample",
        action="store_true",
        help="Generate a sample audio file and test transcription"
    )
    parser.add_argument(
        "--test-websocket",
        action="store_true",
        help="Test WebSocket streaming endpoint"
    )
    parser.add_argument(
        "--skip-health-check",
        action="store_true",
        help="Skip service health check"
    )

    args = parser.parse_args()

    # Show header
    print("\n" + "="*60)
    print("Audio-to-Text Testing Script")
    print("="*60)

    # Check service health
    if not args.skip_health_check:
        is_healthy = await check_service_health()
        if not is_healthy:
            sys.exit(1)

    # Execute tests based on arguments
    if args.generate_sample:
        sample_file = generate_sample_audio()
        await test_transcribe_file(sample_file)

    elif args.file:
        await test_transcribe_file(args.file)

    elif args.test_websocket:
        await test_websocket_streaming()

    else:
        parser.print_help()
        print("\n" + "="*60)
        print("Examples:")
        print("  python test_audio_transcription.py --generate-sample")
        print("  python test_audio_transcription.py --file audio.wav")
        print("  python test_audio_transcription.py --test-websocket")
        print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
