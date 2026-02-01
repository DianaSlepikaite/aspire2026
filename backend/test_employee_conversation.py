#!/usr/bin/env python3
"""
Test script for Employee Conversation Service.
Tests the complete employee profile extraction flow.

Usage:
    python test_employee_conversation.py
"""

import asyncio
import json
import httpx


BASE_URL = "http://localhost:8001/api/v1"
TIMEOUT = 30.0


async def start_conversation(employee_name: str = None, employee_email: str = None, employee_id: str = None):
    """Start a new employee conversation."""
    print("\n" + "="*60)
    print("STEP 1: Start Conversation")
    print("="*60)

    request_data = {}
    if employee_name:
        request_data["employee_name"] = employee_name
    if employee_email:
        request_data["employee_email"] = employee_email
    if employee_id:
        request_data["employee_id"] = employee_id

    print(f"\n📝 Starting conversation...")
    if employee_name:
        print(f"   Name: {employee_name}")
    if employee_email:
        print(f"   Email: {employee_email}")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/conversation/start",
                json=request_data
            )

        if response.status_code in [200, 201]:
            data = response.json()
            conversation_id = data.get("conversation_id")
            profile_id = data.get("employee_profile_id")
            greeting = data.get("greeting_message")

            print(f"\n✅ Conversation Started!")
            print(f"\n💬 AI Greeting:")
            print(f"   {greeting}")
            print(f"\n📋 Details:")
            print(f"   Conversation ID: {conversation_id}")
            print(f"   Profile ID: {profile_id}")

            return {
                "conversation_id": conversation_id,
                "profile_id": profile_id
            }
        else:
            print(f"\n✗ Failed to start conversation: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


async def send_message(conversation_id: str, message: str):
    """Send a message in the conversation."""
    print(f"\n{'─'*60}")
    print(f"👤 YOU: {message}")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/conversation/{conversation_id}/message",
                json={"message": message}
            )

        if response.status_code == 200:
            data = response.json()
            assistant_msg = data.get("assistant_message")
            completeness = data.get("profile_completeness", 0)
            extraction_updates = data.get("extraction_updates", [])

            print(f"🤖 AI: {assistant_msg}")

            if extraction_updates:
                print(f"\n✨ Extracted Information:")
                for update in extraction_updates:
                    field = update.get("field_name")
                    value = update.get("field_value")
                    print(f"   • {field}: {value}")

            print(f"\n📊 Profile Completeness: {completeness}%")

            return data
        else:
            print(f"\n✗ Failed to send message: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


async def get_conversation_status(conversation_id: str):
    """Get conversation status."""
    print(f"\n{'='*60}")
    print("Conversation Status")
    print(f"{'='*60}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/conversation/{conversation_id}/status"
            )

        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Status: {data.get('status')}")
            print(f"📈 Profile Completeness: {data.get('profile_completeness')}%")
            print(f"💬 Total Messages: {data.get('total_messages')}")
            print(f"⏱  Duration: {data.get('duration_minutes')} minutes")
            print(f"✅ Can Complete: {data.get('can_complete')}")

            if data.get('missing_fields'):
                print(f"\n⚠️  Missing Information:")
                for field in data['missing_fields']:
                    print(f"   • {field}")

            return data
        else:
            print(f"✗ Failed to get status: {response.status_code}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


async def complete_conversation(conversation_id: str):
    """Complete the conversation."""
    print(f"\n{'='*60}")
    print("COMPLETING CONVERSATION")
    print(f"{'='*60}")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/conversation/{conversation_id}/complete"
            )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Conversation Completed!")
            print(f"\n📝 Summary:")
            print(f"   {data.get('summary', 'No summary available')}")
            print(f"\n📊 Final Completeness: {data.get('profile_completeness')}%")

            return data
        else:
            print(f"\n✗ Failed to complete: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


async def get_employee_profile(profile_id: str):
    """Get the employee profile."""
    print(f"\n{'='*60}")
    print("EMPLOYEE PROFILE")
    print(f"{'='*60}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/employee-profiles/{profile_id}"
            )

        if response.status_code == 200:
            profile = response.json()

            print(f"\n👤 Employee Information:")
            print(f"   Name: {profile.get('employee_name', 'N/A')}")
            print(f"   Email: {profile.get('employee_email', 'N/A')}")
            print(f"   ID: {profile.get('employee_id', 'N/A')}")

            if profile.get('location'):
                print(f"   Location: {profile['location']}")

            print(f"\n💼 Career:")
            print(f"   Track: {profile.get('career_track', 'N/A')}")
            print(f"   Level: {profile.get('experience_level', 'N/A')}")
            print(f"   Years at PS: {profile.get('years_at_ps', 'N/A')}")
            print(f"   Total Experience: {profile.get('years_total_experience', 'N/A')}")

            if profile.get('technical_skills'):
                print(f"\n🛠️  Technical Skills:")
                skills = profile['technical_skills']
                if isinstance(skills, list):
                    for skill in skills[:10]:  # Show first 10
                        print(f"   • {skill}")
                else:
                    print(f"   {skills}")

            if profile.get('soft_skills'):
                print(f"\n💡 Soft Skills:")
                skills = profile['soft_skills']
                if isinstance(skills, list):
                    for skill in skills[:5]:
                        print(f"   • {skill}")
                else:
                    print(f"   {skills}")

            if profile.get('career_goals'):
                print(f"\n🎯 Career Goals:")
                print(f"   {profile['career_goals']}")

            if profile.get('bench_status'):
                print(f"\n📅 Availability:")
                print(f"   Status: {profile['bench_status']}")
                print(f"   Available: {profile.get('availability_date', 'N/A')}")

            print(f"\n📊 Profile Completeness: {profile.get('profile_completeness_score', 0)}%")

            return profile
        else:
            print(f"✗ Failed to get profile: {response.status_code}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


async def check_service_health():
    """Check if service is running."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                return True
    except:
        pass
    return False


async def main():
    """Run a complete test conversation."""
    print("\n" + "="*60)
    print("Employee Conversation Service - Test Script")
    print("="*60)

    # Check service
    print("\n⏳ Checking service...")
    if not await check_service_health():
        print("\n✗ Employee service is not running!")
        print("\nTo start the service:")
        print("  cd backend")
        print("  uvicorn employee_conversation_service.main:app --port 8001 --reload")
        return

    print("✓ Service is healthy\n")

    # Start conversation
    conversation = await start_conversation(
        employee_name="John Smith",
        employee_email="john.smith@company.com"
    )

    if not conversation:
        print("\n❌ Failed to start conversation")
        return

    conversation_id = conversation["conversation_id"]
    profile_id = conversation["profile_id"]

    # Simulate conversation
    print(f"\n{'='*60}")
    print("STEP 2: Conversation Exchange")
    print(f"{'='*60}")

    # Message 1: Introduce experience
    await send_message(
        conversation_id,
        "Hi! I'm a Senior Software Engineer with 8 years of experience. "
        "I specialize in Python, JavaScript, and cloud technologies like AWS and Azure."
    )

    # Message 2: Share current role
    await send_message(
        conversation_id,
        "I'm currently on the bench after rolling off a fintech project. "
        "I was the technical lead on a payment processing system using microservices."
    )

    # Message 3: Career goals
    await send_message(
        conversation_id,
        "I'm looking to work on AI/ML projects next. I've been taking courses on "
        "machine learning and would love to transition into a data engineering role."
    )

    # Message 4: Skills
    await send_message(
        conversation_id,
        "My key technical skills include: Python, React, Node.js, PostgreSQL, "
        "Docker, Kubernetes, AWS Lambda, and CI/CD with GitHub Actions. "
        "I'm also experienced with Agile methodologies and leading small teams."
    )

    # Get status
    await asyncio.sleep(1)
    status = await get_conversation_status(conversation_id)

    # Complete conversation
    if status and status.get('can_complete'):
        await complete_conversation(conversation_id)

    # Get final profile
    await get_employee_profile(profile_id)

    # Summary
    print(f"\n{'='*60}")
    print("✅ TEST COMPLETE")
    print(f"{'='*60}")
    print(f"\n🎯 Results:")
    print(f"   • Conversation created successfully")
    print(f"   • AI extracted skills and experience")
    print(f"   • Profile completeness calculated")
    print(f"   • Conversation completed")
    print(f"\n💡 Next Steps:")
    print(f"   • View profile: GET {BASE_URL}/employee-profiles/{profile_id}")
    print(f"   • Test in Swagger: http://localhost:8001/docs")
    print(f"   • Upload resume: POST {BASE_URL}/document/upload")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
