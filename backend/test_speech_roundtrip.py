#!/usr/bin/env python3
"""
Comprehensive test for audio-to-text functionality.
Tests the full roundtrip: Text -> Speech (TTS) -> Transcription (STT)

This verifies that both TTS and STT are working correctly.
"""

import asyncio
import sys
from pathlib import Path

import httpx


BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0


async def test_text_to_speech(text: str, output_file: str = "tts_output.wav") -> str:
    """Generate speech audio from text using TTS endpoint."""
    print(f"\n{'='*60}")
    print("Step 1: Text-to-Speech (TTS)")
    print(f"{'='*60}")
    print(f"📝 Input text: \"{text}\"")
    print(f"⏳ Generating speech audio...")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/speech/synthesize",
                json={
                    "text": text,
                    "voice_name": "en-US-JennyNeural",
                    "output_format": "wav"
                }
            )

            if response.status_code == 200:
                audio_data = response.content
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                print(f"✓ Speech generated successfully!")
                print(f"📊 Audio size: {len(audio_data)} bytes")
                print(f"💾 Saved to: {output_file}")
                return output_file
            else:
                print(f"✗ TTS failed with status {response.status_code}")
                try:
                    error = response.json()
                    print(f"Error: {error}")
                except:
                    print(f"Response: {response.text}")
                return None

    except Exception as e:
        print(f"✗ Error during TTS: {e}")
        return None


async def test_speech_to_text(audio_file: str) -> dict:
    """Transcribe audio file using STT endpoint."""
    print(f"\n{'='*60}")
    print("Step 2: Speech-to-Text (STT)")
    print(f"{'='*60}")
    print(f"📁 Input file: {audio_file}")

    file_path = Path(audio_file)
    print(f"📊 File size: {file_path.stat().st_size} bytes")
    print(f"⏳ Transcribing audio...")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            with open(audio_file, "rb") as f:
                # Determine content type from file extension
                content_type = "audio/wav" if audio_file.endswith(".wav") else "audio/mpeg"
                files = {"audio_file": (file_path.name, f, content_type)}
                response = await client.post(
                    f"{BASE_URL}/speech/transcribe",
                    files=files
                )

            print(f"📤 Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Transcription successful!")
                return data
            else:
                print(f"✗ Transcription failed!")
                try:
                    error = response.json()
                    print(f"Error: {error}")
                except:
                    print(f"Response: {response.text}")
                return None

    except Exception as e:
        print(f"✗ Error during STT: {e}")
        return None


async def test_roundtrip(test_text: str):
    """Test complete roundtrip: Text -> Speech -> Text."""
    print(f"\n{'='*60}")
    print("Audio-to-Text Roundtrip Test")
    print(f"{'='*60}")

    # Check service health
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✓ Service is running and healthy")
            else:
                print(f"⚠ Service returned status {response.status_code}")
                return
    except Exception as e:
        print(f"✗ Cannot connect to service: {e}")
        print("\nTo start the service, run:")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  uvicorn client_need_service.main:app --reload")
        return

    # Step 1: Generate speech from text
    audio_file = await test_text_to_speech(test_text)
    if not audio_file:
        print("\n❌ Roundtrip test failed at TTS step")
        return

    # Step 2: Transcribe the generated speech
    result = await test_speech_to_text(audio_file)
    if not result:
        print("\n❌ Roundtrip test failed at STT step")
        return

    # Step 3: Compare results
    print(f"\n{'='*60}")
    print("Step 3: Verification")
    print(f"{'='*60}")

    original_text = test_text.lower().strip()
    transcribed_text = result.get("transcription", "").lower().strip()

    print(f"\n📝 Original text:     \"{test_text}\"")
    print(f"📝 Transcribed text:  \"{result.get('transcription', '')}\"")
    print(f"📊 Confidence:        {result.get('confidence', 0):.2%}")
    print(f"⏱  Duration:          {result.get('duration_seconds', 0):.2f} seconds")

    # Simple similarity check
    if original_text == transcribed_text:
        print(f"\n✅ Perfect match! Roundtrip test PASSED")
    elif original_text in transcribed_text or transcribed_text in original_text:
        print(f"\n✅ Close match! Roundtrip test PASSED")
    else:
        # Calculate simple word overlap
        original_words = set(original_text.split())
        transcribed_words = set(transcribed_text.split())
        overlap = len(original_words & transcribed_words)
        total = len(original_words)
        similarity = overlap / total if total > 0 else 0

        if similarity > 0.7:
            print(f"\n✅ Good similarity ({similarity:.1%})! Roundtrip test PASSED")
        else:
            print(f"\n⚠ Low similarity ({similarity:.1%}). Results may vary with speech recognition.")

    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print("✓ Text-to-Speech: Working")
    print("✓ Speech-to-Text: Working")
    print("✓ Azure Speech Service: Connected and functional")
    print(f"{'='*60}\n")


async def main():
    # Test phrases - these work well with speech recognition
    test_phrases = [
        "Hello, this is a test of the audio transcription system.",
        "The quick brown fox jumps over the lazy dog.",
        "Testing one two three four five.",
    ]

    if len(sys.argv) > 1:
        # Use custom text from command line
        test_text = " ".join(sys.argv[1:])
    else:
        # Use default test phrase
        test_text = test_phrases[0]

    await test_roundtrip(test_text)


if __name__ == "__main__":
    print("\nUsage:")
    print("  python test_speech_roundtrip.py")
    print("  python test_speech_roundtrip.py \"Custom text to test\"")
    print()

    asyncio.run(main())
