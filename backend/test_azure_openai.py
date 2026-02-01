"""
Test script to verify Azure OpenAI connection and GPT-4 deployment
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

print("🔧 Testing Azure OpenAI Connection...\n")

# Get credentials from .env
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print(f"✓ Endpoint: {endpoint}")
print(f"✓ Deployment: {deployment_name}")
print(f"✓ API Version: {api_version}")
print(f"✓ API Key: {'*' * 20}{api_key[-10:] if api_key else 'NOT SET'}\n")

try:
    # Create Azure OpenAI client
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )

    print("📡 Sending test message to GPT-4...\n")

    # Test with a simple message
    response = client.chat.completions.create(
        model=deployment_name,  # This should match your deployment name
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from Azure OpenAI!' in one sentence."}
        ],
        max_tokens=50,
        temperature=0.7
    )

    # Extract response
    message = response.choices[0].message.content
    tokens_used = response.usage.total_tokens

    print("✅ SUCCESS! Azure OpenAI is working!\n")
    print(f"🤖 GPT-4 Response: {message}")
    print(f"📊 Tokens used: {tokens_used}")
    print(f"💰 Estimated cost: ~${tokens_used * 0.00006:.4f}\n")

    print("🎉 Your Azure OpenAI setup is complete and working!")

except Exception as e:
    print(f"❌ ERROR: {e}\n")
    print("🔍 Troubleshooting:")
    print("  1. Check if GPT-4 model is deployed in Azure Portal")
    print("  2. Verify deployment name matches AZURE_OPENAI_DEPLOYMENT_NAME in .env")
    print("  3. Ensure API key and endpoint are correct")
    print("  4. Check if you have quota/permissions for GPT-4")
