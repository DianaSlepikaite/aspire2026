#!/usr/bin/env python3
import asyncio
import httpx

async def list_intakes():
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("http://localhost:8000/api/v1/intake?limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"\n{'='*80}")
            print(f"Recent Intake Packages (Total: {data.get('total', 0)})")
            print(f"{'='*80}")
            for item in data.get('items', []):
                print(f"\nID: {item.get('id')}")
                print(f"   Source: {item.get('source_type')} | Status: {item.get('status')}")
                print(f"   Client: {item.get('client_name', 'N/A')} ({item.get('client_email', 'N/A')})")
                print(f"   Created: {item.get('created_at')}")
                if item.get('normalized_content'):
                    preview = str(item['normalized_content'])[:100]
                    print(f"   Preview: {preview}...")
            print(f"\n{'='*80}\n")
        else:
            print(f"Error: {response.status_code}")

asyncio.run(list_intakes())
