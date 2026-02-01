#!/usr/bin/env python3
"""
Check what's in an intake package to see the transcription.
Usage: python check_intake.py <intake_id>
"""

import asyncio
import sys
import json
import httpx

BASE_URL = "http://localhost:8000/api/v1"

async def check_intake(intake_id: str):
    """Get and display intake package details."""

    print(f"\n{'='*60}")
    print(f"Checking Intake Package: {intake_id}")
    print(f"{'='*60}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/intake/{intake_id}")

        if response.status_code == 200:
            intake = response.json()

            print(f"\n✅ Intake Package Found")
            print(f"\n{'='*60}")
            print("BASIC INFO")
            print(f"{'='*60}")
            print(f"ID: {intake.get('id')}")
            print(f"Status: {intake.get('status')}")
            print(f"Source Type: {intake.get('source_type')}")
            print(f"Client Name: {intake.get('client_name')}")
            print(f"Client Email: {intake.get('client_email')}")
            print(f"Created: {intake.get('created_at')}")

            # Raw content (original transcription)
            if intake.get('raw_content'):
                print(f"\n{'='*60}")
                print("RAW CONTENT (Original Transcription)")
                print(f"{'='*60}")
                print(intake['raw_content'])
            else:
                print(f"\n⚠️  No raw content found")

            # Normalized content
            if intake.get('normalized_content'):
                print(f"\n{'='*60}")
                print("NORMALIZED CONTENT")
                print(f"{'='*60}")
                norm = intake['normalized_content']
                if isinstance(norm, str):
                    print(norm)
                elif isinstance(norm, dict):
                    print(f"Text: {norm.get('text', 'N/A')}")
                    print(f"Word Count: {norm.get('word_count', 0)}")
                    print(f"Language: {norm.get('language', 'N/A')}")
                    if norm.get('sections'):
                        print(f"\nSections: {len(norm['sections'])}")
                        for i, section in enumerate(norm['sections'][:3], 1):
                            print(f"  {i}. {section.get('title', 'Untitled')}: {section.get('content', '')[:100]}...")
            else:
                print(f"\n⚠️  No normalized content found")

            # Audit trail
            if intake.get('audit_trail'):
                print(f"\n{'='*60}")
                print("AUDIT TRAIL")
                print(f"{'='*60}")
                for entry in intake['audit_trail']:
                    print(f"• [{entry.get('step')}] {entry.get('action')}")
                    if entry.get('word_count'):
                        print(f"  Word count: {entry['word_count']}")
                    if entry.get('confidence'):
                        print(f"  Confidence: {entry['confidence']:.2%}")
                    if entry.get('duration_seconds'):
                        print(f"  Duration: {entry['duration_seconds']:.2f}s")
                    if entry.get('error'):
                        print(f"  Error: {entry['error']}")

            # Metadata
            if intake.get('metadata'):
                print(f"\n{'='*60}")
                print("METADATA")
                print(f"{'='*60}")
                meta = intake['metadata']
                print(f"File: {meta.get('file_name')}")
                print(f"Size: {meta.get('file_size_bytes', 0):,} bytes")
                print(f"MIME: {meta.get('mime_type')}")
                if meta.get('tags'):
                    print(f"Tags: {', '.join(meta['tags'])}")

            print(f"\n{'='*60}\n")

            return intake

        elif response.status_code == 404:
            print(f"\n✗ Intake package not found: {intake_id}")
            return None
        else:
            print(f"\n✗ Error: Status {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None

async def main():
    if len(sys.argv) < 2:
        print("\nUsage: python check_intake.py <intake_id>")
        print("\nExample:")
        print("  python check_intake.py 123e4567-e89b-12d3-a456-426614174000")
        return

    intake_id = sys.argv[1]
    await check_intake(intake_id)

if __name__ == "__main__":
    asyncio.run(main())
