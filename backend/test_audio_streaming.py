#!/usr/bin/env python3
"""
Test WebSocket audio streaming with real-time transcription.

This script can:
1. Stream audio from a file (simulating real-time input)
2. Connect to the WebSocket endpoint and receive transcriptions

Usage:
    python test_audio_streaming.py <audio_file.wav>
"""

import asyncio
import json
import sys
import wave
from pathlib import Path

try:
    import websockets
except ImportError:
    print("Error: websockets library required")
    print("Install with: pip install websockets")
    sys.exit(1)


WS_URL = "ws://localhost:8000/api/v1/speech/stream"


async def stream_audio_file(audio_file_path: str, language: str = "en-US"):
    """Stream audio file to WebSocket endpoint and receive transcriptions."""

    print("\n" + "="*60)
    print("WebSocket Audio Streaming Test")
    print("="*60)

    file_path = Path(audio_file_path)

    if not file_path.exists():
        print(f"\n✗ File not found: {audio_file_path}")
        return

    print(f"\n📁 File: {file_path.name}")
    print(f"📊 Size: {file_path.stat().st_size:,} bytes")
    print(f"🌐 Language: {language}")

    # Read WAV file
    try:
        with wave.open(str(file_path), 'rb') as wav_file:
            # Get audio parameters
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()

            print(f"\n🎵 Audio Info:")
            print(f"   Channels: {channels}")
            print(f"   Sample Width: {sample_width} bytes")
            print(f"   Frame Rate: {framerate} Hz")
            print(f"   Duration: {n_frames / framerate:.2f} seconds")

            if framerate != 16000 or sample_width != 2 or channels != 1:
                print(f"\n⚠️  Warning: Audio should be 16kHz, 16-bit, mono PCM for best results")
                print(f"   Current: {framerate}Hz, {sample_width*8}-bit, {channels} channel(s)")

            # Read all audio data
            audio_data = wav_file.readframes(n_frames)

    except Exception as e:
        print(f"\n✗ Error reading audio file: {e}")
        print("\n💡 Tip: File must be a valid WAV file")
        return

    # Connect to WebSocket
    print(f"\n⏳ Connecting to {WS_URL}...")

    try:
        async with websockets.connect(f"{WS_URL}?language={language}") as websocket:
            print("✓ Connected!")

            # Wait for session_started
            session_msg = await websocket.recv()
            session_data = json.loads(session_msg)

            if session_data.get("type") == "session_started":
                session_id = session_data.get("session_id")
                print(f"\n🎙️  Session Started")
                print(f"   Session ID: {session_id}")
                print(f"   Language: {session_data.get('language')}")

                print(f"\n{'='*60}")
                print("STREAMING AUDIO")
                print(f"{'='*60}")

                # Stream audio in chunks (simulate real-time streaming)
                chunk_size = 3200  # 100ms chunks at 16kHz, 16-bit, mono
                total_chunks = len(audio_data) // chunk_size

                print(f"\n📤 Streaming {total_chunks} chunks...")

                # Create task to receive transcriptions
                transcriptions = []

                async def receive_transcriptions():
                    """Receive and display transcriptions."""
                    try:
                        while True:
                            message = await websocket.recv()
                            data = json.loads(message)

                            if data.get("type") == "transcript":
                                transcript = data.get("text", "")
                                is_final = data.get("is_final", False)
                                confidence = data.get("confidence", 0)

                                status = "FINAL" if is_final else "interim"
                                print(f"\n[{status}] {transcript}")
                                if is_final:
                                    print(f"         Confidence: {confidence:.2%}")
                                    transcriptions.append(transcript)

                            elif data.get("type") == "session_stopped":
                                print(f"\n{'='*60}")
                                print("SESSION STOPPED")
                                print(f"{'='*60}")
                                print(f"Duration: {data.get('duration_seconds', 0):.2f}s")
                                print(f"Transcripts: {data.get('transcript_count', 0)}")
                                break

                            elif data.get("type") == "error":
                                print(f"\n✗ Error: {data.get('message')}")
                                break
                    except websockets.exceptions.ConnectionClosed:
                        pass

                # Start receiving task
                receive_task = asyncio.create_task(receive_transcriptions())

                # Stream audio chunks
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i + chunk_size]
                    await websocket.send(chunk)

                    # Progress indicator
                    chunk_num = i // chunk_size + 1
                    if chunk_num % 10 == 0:
                        print(f"   Sent {chunk_num}/{total_chunks} chunks...")

                    # Simulate real-time streaming (100ms per chunk)
                    await asyncio.sleep(0.1)

                print(f"   ✓ All chunks sent!")

                # Stop the session
                print(f"\n⏳ Stopping session...")
                await websocket.send(json.dumps({"type": "stop_session"}))

                # Wait for final transcriptions
                await receive_task

                # Summary
                if transcriptions:
                    print(f"\n{'='*60}")
                    print("COMPLETE TRANSCRIPTION")
                    print(f"{'='*60}")
                    full_text = " ".join(transcriptions)
                    print(f"\n{full_text}")
                    print(f"\n📊 Total segments: {len(transcriptions)}")
                    print(f"📊 Total words: {len(full_text.split())}")
                    print(f"{'='*60}\n")
                else:
                    print(f"\n⚠️  No transcriptions received")
                    print(f"   This may happen if:")
                    print(f"   • Audio format is incorrect (needs 16kHz, 16-bit, mono PCM)")
                    print(f"   • No speech detected in audio")
                    print(f"   • Audio quality is too poor")

            else:
                print(f"\n✗ Unexpected response: {session_data}")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"\n✗ Connection failed: {e}")
        print(f"   Is the service running on http://localhost:8000?")
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def main():
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("WebSocket Audio Streaming Test")
        print("="*60)
        print("\nUsage:")
        print("  python test_audio_streaming.py <audio_file.wav> [language]")
        print("\nExamples:")
        print("  python test_audio_streaming.py recording.wav")
        print("  python test_audio_streaming.py meeting.wav en-US")
        print("\nRequirements:")
        print("  • Audio must be WAV format")
        print("  • Recommended: 16kHz, 16-bit, mono PCM")
        print("  • Service must be running on http://localhost:8000")
        print("\n" + "="*60)
        print("\n💡 Quick Audio Conversion:")
        print("   If your audio is not in the right format:")
        print("   ffmpeg -i input.wav -ar 16000 -ac 1 -sample_fmt s16 output.wav")
        print("="*60 + "\n")
        return

    audio_file = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "en-US"

    await stream_audio_file(audio_file, language)


if __name__ == "__main__":
    asyncio.run(main())
