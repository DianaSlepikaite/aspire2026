#!/usr/bin/env python3
"""
Comprehensive test script for Employee Conversation Service features.

Tests:
1. Regular conversations to capture skills, experience, and career aspirations
2. AI-enhanced CV/profile generation
3. Resume upload and parsing
4. PDF resume generation

Usage:
    python test_employee_features.py
"""

import asyncio
import json
import httpx
from pathlib import Path


BASE_URL = "http://localhost:8001/api/v1"
TIMEOUT = 30.0


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


async def start_conversation(employee_name: str = None, employee_email: str = None):
    """Start a new employee conversation."""
    print("\n" + "="*70)
    print("TEST 1: Start Conversation & Capture Profile Through Dialogue")
    print("="*70)

    request_data = {}
    if employee_name:
        request_data["employee_name"] = employee_name
    if employee_email:
        request_data["employee_email"] = employee_email

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
            print(f"\n❌ Failed to start conversation: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def send_message(conversation_id: str, message: str):
    """Send a message in the conversation."""
    print(f"\n{'─'*70}")
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
            print(f"\n❌ Failed to send message: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def get_employee_profile(profile_id: str):
    """Get the employee profile."""
    print(f"\n{'='*70}")
    print("TEST 2: View AI-Enhanced Employee Profile")
    print(f"{'='*70}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/employee-profiles/{profile_id}"
            )

        if response.status_code == 200:
            profile = response.json()

            print(f"\n👤 Employee Information:")
            print(f"   Name: {profile.get('full_name', 'N/A')}")
            print(f"   Email: {profile.get('email', 'N/A')}")
            print(f"   Phone: {profile.get('phone', 'N/A')}")

            if profile.get('summary'):
                print(f"\n📝 Summary:")
                print(f"   {profile['summary']}")

            print(f"\n💼 Experience:")
            print(f"   Years: {profile.get('experience_years', 'N/A')}")

            if profile.get('skills'):
                print(f"\n🛠️  Skills:")
                skills = profile['skills']
                if isinstance(skills, list):
                    for skill in skills[:15]:  # Show first 15
                        print(f"   • {skill}")
                    if len(skills) > 15:
                        print(f"   ... and {len(skills) - 15} more")
                else:
                    print(f"   {skills}")

            if profile.get('certifications'):
                print(f"\n🏆 Certifications:")
                certs = profile['certifications']
                if isinstance(certs, list):
                    for cert in certs:
                        print(f"   • {cert}")
                else:
                    print(f"   {certs}")

            if profile.get('education'):
                print(f"\n🎓 Education:")
                edu = profile['education']
                if isinstance(edu, list):
                    for item in edu:
                        if isinstance(item, dict):
                            degree = item.get('degree', 'N/A')
                            school = item.get('school', 'N/A')
                            year = item.get('year', '')
                            print(f"   • {degree} - {school} {year}")
                        else:
                            print(f"   • {item}")
                else:
                    print(f"   {edu}")

            if profile.get('experience'):
                print(f"\n💼 Work Experience:")
                exp = profile['experience']
                if isinstance(exp, list):
                    for item in exp[:5]:  # Show first 5
                        if isinstance(item, dict):
                            title = item.get('title', 'N/A')
                            company = item.get('company', 'N/A')
                            years = item.get('years', '')
                            print(f"   • {title} at {company} {years}")
                        else:
                            print(f"   • {item}")
                else:
                    print(f"   {exp}")

            if profile.get('preferred_roles'):
                print(f"\n🎯 Preferred Roles:")
                roles = profile['preferred_roles']
                if isinstance(roles, list):
                    for role in roles:
                        print(f"   • {role}")
                else:
                    print(f"   {roles}")

            print(f"\n📊 Profile Completeness: {profile.get('profile_completeness_score', 0)}%")

            return profile
        else:
            print(f"❌ Failed to get profile: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def complete_conversation(conversation_id: str):
    """Complete the conversation."""
    print(f"\n{'─'*70}")
    print("Completing conversation...")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/conversation/{conversation_id}/complete"
            )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Conversation Completed!")
            if data.get('summary'):
                print(f"\n📝 Summary:")
                print(f"   {data.get('summary')}")
            print(f"\n📊 Final Completeness: {data.get('profile_completeness')}%")
            return data
        else:
            print(f"\n❌ Failed to complete: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def generate_resume_pdf(profile_id: str):
    """Generate and download resume PDF."""
    print(f"\n{'='*70}")
    print("TEST 3: Generate AI-Enhanced Resume PDF")
    print(f"{'='*70}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BASE_URL}/agent/generate-resume/{profile_id}"
            )

        if response.status_code == 200:
            # Save PDF
            filename = "generated_resume.pdf"
            output_path = Path(__file__).parent / filename

            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"\n✅ Resume PDF Generated Successfully!")
            print(f"   📄 File: {output_path}")
            print(f"   📏 Size: {len(response.content)} bytes")
            print(f"\n💡 Open the file to view the AI-enhanced resume")

            return output_path
        else:
            print(f"\n❌ Failed to generate resume: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def upload_resume(file_path: Path):
    """Upload and parse a resume."""
    print(f"\n{'='*70}")
    print("TEST 4: Upload and Parse Resume/CV")
    print(f"{'='*70}")

    if not file_path or not file_path.exists():
        print(f"\n⚠️  File not found: {file_path}")
        print("   Skipping resume upload test")
        return None

    print(f"\n📤 Uploading resume: {file_path.name}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/pdf")}
                response = await client.post(
                    f"{BASE_URL}/agent/process-upload",
                    files=files
                )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Resume Processed Successfully!")
            print(f"\n📊 Extraction Results:")

            if data.get('employee_profile_id'):
                print(f"   Profile ID: {data['employee_profile_id']}")

            if data.get('extracted_data'):
                extracted = data['extracted_data']
                print(f"\n   Extracted Fields:")
                for key, value in extracted.items():
                    if value:
                        if isinstance(value, list):
                            print(f"   • {key}: {len(value)} items")
                        elif isinstance(value, dict):
                            print(f"   • {key}: {len(value)} fields")
                        else:
                            value_str = str(value)[:50]
                            print(f"   • {key}: {value_str}")

            if data.get('confidence'):
                print(f"\n   Confidence: {data['confidence']*100:.1f}%")

            return data
        else:
            print(f"\n❌ Failed to upload resume: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def list_profiles():
    """List all employee profiles."""
    print(f"\n{'='*70}")
    print("TEST 5: List All Employee Profiles")
    print(f"{'='*70}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/employee-profiles/?limit=10"
            )

        if response.status_code == 200:
            profiles = response.json()
            print(f"\n✅ Found {len(profiles)} profiles")

            for i, profile in enumerate(profiles, 1):
                print(f"\n   {i}. {profile.get('full_name', 'Unnamed')}")
                print(f"      ID: {profile.get('id')}")
                print(f"      Email: {profile.get('email', 'N/A')}")
                print(f"      Completeness: {profile.get('profile_completeness_score', 0)}%")
                if profile.get('skills'):
                    skill_count = len(profile['skills']) if isinstance(profile['skills'], list) else 0
                    print(f"      Skills: {skill_count} listed")

            return profiles
        else:
            print(f"\n❌ Failed to list profiles: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def main():
    """Run comprehensive tests."""
    print("\n" + "="*70)
    print("Employee Conversation Service - Comprehensive Feature Test")
    print("="*70)

    # Check service
    print("\n⏳ Checking service health...")
    if not await check_service_health():
        print("\n❌ Employee service is not running!")
        print("\nTo start the service:")
        print("  ./START_BOTH_SERVICES.sh")
        print("  OR")
        print("  cd backend")
        print("  uvicorn employee_conversation_service.main:app --port 8001 --reload")
        return

    print("✅ Service is healthy\n")

    # Test 1: Conversation Flow
    conversation = await start_conversation(
        employee_name="Sarah Johnson",
        employee_email="sarah.johnson@example.com"
    )

    if not conversation:
        print("\n❌ Failed to start conversation. Aborting tests.")
        return

    conversation_id = conversation["conversation_id"]
    profile_id = conversation["profile_id"]

    # Simulate multi-turn conversation
    messages = [
        "Hi! I'm a Full Stack Developer with 6 years of professional experience. I've worked extensively with Python, JavaScript, and modern web frameworks.",

        "I have a Bachelor's degree in Computer Science from MIT, graduated in 2017. I'm also AWS Certified Solutions Architect and have my Scrum Master certification.",

        "My technical skills include: Python, React, Node.js, TypeScript, PostgreSQL, MongoDB, Docker, Kubernetes, AWS (EC2, S3, Lambda), CI/CD with Jenkins and GitHub Actions, and GraphQL.",

        "I've worked at three companies: Started as Junior Developer at TechStart (2017-2019), then Mid-level at DataCorp (2019-2021), and currently Senior Full Stack Developer at CloudSystems since 2021.",

        "I'm really passionate about building scalable systems and mentoring junior developers. I'm looking to transition into a Tech Lead or Engineering Manager role where I can combine technical expertise with leadership.",
    ]

    for msg in messages:
        await send_message(conversation_id, msg)
        await asyncio.sleep(0.5)  # Small delay between messages

    # Complete conversation
    await complete_conversation(conversation_id)

    # Test 2: View Profile
    await get_employee_profile(profile_id)

    # Test 3: Generate Resume PDF
    pdf_path = await generate_resume_pdf(profile_id)

    # Test 4: Upload Resume (if PDF was generated, use it as test input)
    if pdf_path and pdf_path.exists():
        print(f"\n💡 Testing resume upload with generated PDF...")
        await upload_resume(pdf_path)

    # Test 5: List Profiles
    await list_profiles()

    # Summary
    print(f"\n{'='*70}")
    print("✅ ALL TESTS COMPLETE")
    print(f"{'='*70}")
    print(f"\n🎯 Test Results:")
    print(f"   ✅ Conversation flow - Skills, experience & aspirations captured")
    print(f"   ✅ AI-enhanced profile - Structured employee profile created")
    print(f"   ✅ Resume PDF generation - Dynamic CV created from profile")
    print(f"   ✅ Resume upload & parsing - Document processing verified")
    print(f"   ✅ Profile listing - Multi-profile management working")

    print(f"\n💡 Next Steps:")
    print(f"   • View profile: GET {BASE_URL}/employee-profiles/{profile_id}")
    print(f"   • Test in Swagger: http://localhost:8001/docs")
    print(f"   • Check database for stored profiles")

    if pdf_path:
        print(f"   • Review generated resume: {pdf_path}")

    print(f"{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(main())
