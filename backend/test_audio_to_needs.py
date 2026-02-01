#!/usr/bin/env python3
"""
End-to-end test: Audio → Transcription → Need Extraction

This script tests the complete pipeline:
1. Upload audio file for transcription
2. Audio is transcribed and stored as intake package
3. Process intake package with Client Need Agent
4. Display extracted client needs

Usage:
    python test_audio_to_needs.py <audio_file>
    python test_audio_to_needs.py recording.wav
"""

import asyncio
import sys
import json
from pathlib import Path

import httpx


BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 60.0


async def upload_audio_for_intake(audio_file_path: str, client_name: str = None, client_email: str = None):
    """Step 1: Upload audio file to intake endpoint."""
    print("\n" + "="*60)
    print("STEP 1: Upload Audio for Intake")
    print("="*60)

    file_path = Path(audio_file_path)

    if not file_path.exists():
        print(f"✗ File not found: {audio_file_path}")
        return None

    content_types = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".mp4": "video/mp4",
    }
    content_type = content_types.get(file_path.suffix.lower(), "audio/wav")

    print(f"📁 File: {file_path.name}")
    print(f"📊 Size: {file_path.stat().st_size:,} bytes")
    print(f"📋 Type: {content_type}")
    print(f"\n⏳ Uploading and transcribing...")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            with open(audio_file_path, "rb") as f:
                files = {"file": (file_path.name, f, content_type)}
                data = {}
                if client_name:
                    data["client_name"] = client_name
                if client_email:
                    data["client_email"] = client_email

                response = await client.post(
                    f"{BASE_URL}/intake/upload/audio",
                    files=files,
                    data=data
                )

        if response.status_code == 201:
            intake_data = response.json()
            intake_id = intake_data.get("id")

            print(f"\n✅ SUCCESS - Audio Intake Complete")
            print(f"\n📦 Intake Package ID: {intake_id}")
            print(f"📝 Status: {intake_data.get('status')}")
            print(f"🔤 Source Type: {intake_data.get('source_type')}")

            if intake_data.get("normalized_content"):
                preview = intake_data["normalized_content"][:200]
                print(f"\n📄 Transcription Preview:")
                print(f"   {preview}...")

            return intake_id
        else:
            print(f"\n✗ Upload failed with status {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {json.dumps(error, indent=2)}")
            except:
                print(f"Response: {response.text}")
            return None

    except httpx.TimeoutException:
        print(f"\n✗ Request timed out after {TIMEOUT} seconds")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


async def process_with_agent(intake_id: str, user_query: str = None):
    """Step 2: Process intake package with Client Need Agent."""
    print("\n" + "="*60)
    print("STEP 2: Extract Needs with Client Need Agent")
    print("="*60)

    print(f"🤖 Processing intake package: {intake_id}")
    if user_query:
        print(f"📋 Custom query: {user_query}")
    print(f"\n⏳ Agent is analyzing...")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            payload = {"intake_id": intake_id}
            if user_query:
                payload["user_query"] = user_query

            response = await client.post(
                f"{BASE_URL}/agent/process-intake",
                json=payload
            )

        if response.status_code == 200:
            agent_result = response.json()

            print(f"\n✅ SUCCESS - Need Extraction Complete")
            print(f"\n{'='*60}")
            print("AGENT OUTPUT")
            print(f"{'='*60}")
            print(agent_result.get("output", "No output"))

            if agent_result.get("intermediate_steps"):
                print(f"\n{'='*60}")
                print("INTERMEDIATE STEPS")
                print(f"{'='*60}")
                for i, step in enumerate(agent_result["intermediate_steps"], 1):
                    print(f"\n{i}. {step}")

            return agent_result
        else:
            print(f"\n✗ Agent processing failed with status {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {json.dumps(error, indent=2)}")
            except:
                print(f"Response: {response.text}")
            return None

    except httpx.TimeoutException:
        print(f"\n✗ Request timed out after {TIMEOUT} seconds")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


async def get_intake_package_details(intake_id: str):
    """Optional: Get detailed intake package information."""
    print("\n" + "="*60)
    print("BONUS: Intake Package Details")
    print("="*60)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/intake/{intake_id}")

        if response.status_code == 200:
            intake = response.json()
            print(f"\n📦 Package ID: {intake.get('id')}")
            print(f"📅 Created: {intake.get('created_at')}")
            print(f"📝 Status: {intake.get('status')}")
            print(f"👤 Client: {intake.get('client_name', 'N/A')}")
            print(f"📧 Email: {intake.get('client_email', 'N/A')}")

            if intake.get("metadata"):
                meta = intake["metadata"]
                print(f"\n📋 Metadata:")
                print(f"   File: {meta.get('file_name')}")
                print(f"   Size: {meta.get('file_size_bytes', 0):,} bytes")
                print(f"   Type: {meta.get('mime_type')}")

            return intake
        else:
            print(f"✗ Failed to get intake details (status {response.status_code})")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


async def check_service_health():
    """Check if the service is running."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                return True
    except:
        pass
    return False


async def main():
    print("\n" + "="*60)
    print("Audio → Transcription → Need Extraction Pipeline Test")
    print("="*60)

    # Check arguments
    if len(sys.argv) < 2:
        print("\nUsage: python test_audio_to_needs.py <audio_file> [client_name] [client_email]")
        print("\nExamples:")
        print("  python test_audio_to_needs.py recording.wav")
        print('  python test_audio_to_needs.py meeting.mp3 "John Doe" "john@example.com"')
        print("\nSupported formats: WAV, MP3, OGG, M4A, MP4")
        return

    audio_file = sys.argv[1]
    client_name = sys.argv[2] if len(sys.argv) > 2 else None
    client_email = sys.argv[3] if len(sys.argv) > 3 else None

    # Check service
    print("\n⏳ Checking service status...")
    if not await check_service_health():
        print("\n✗ Service is not running!")
        print("\nTo start the service:")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  uvicorn client_need_service.main:app --reload")
        return

    print("✓ Service is healthy\n")

    # Step 1: Upload audio
    intake_id = await upload_audio_for_intake(audio_file, client_name, client_email)
    if not intake_id:
        print("\n❌ Pipeline failed at Step 1 (Audio Upload)")
        return

    # Step 2: Process with agent
    agent_result = await process_with_agent(intake_id)
    if not agent_result:
        print("\n❌ Pipeline failed at Step 2 (Need Extraction)")
        return

    # Optional: Get full intake details
    await get_intake_package_details(intake_id)

    # Summary
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE")
    print("="*60)
    print(f"\n🎯 Results Summary:")
    print(f"   • Audio transcribed and stored")
    print(f"   • Client needs extracted by agent")
    print(f"   • Intake Package ID: {intake_id}")
    print(f"\n💡 Next Steps:")
    print(f"   • Review extracted needs in agent output above")
    print(f"   • Access intake package: GET {BASE_URL}/intake/{intake_id}")
    print(f"   • View in Swagger UI: http://localhost:8000/docs")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
