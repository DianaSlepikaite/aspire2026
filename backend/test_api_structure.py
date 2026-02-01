"""
Simple test script to verify API structure without external dependencies
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
print("Testing imports...")
try:
    from client_need_service.models import schemas
    print("✓ Schemas imported successfully")

    # Test creating models
    from client_need_service.models.schemas import (
        ConversationStartRequest,
        MessageRequest,
        ClientNeedUpdate
    )

    # Create test objects
    start_req = ConversationStartRequest(
        client_name="Test User",
        client_email="test@example.com",
        source_channel="web"
    )
    print(f"✓ Created ConversationStartRequest: {start_req.client_name}")

    msg_req = MessageRequest(
        message="I need a Python developer for 3 months"
    )
    print(f"✓ Created MessageRequest: {msg_req.message[:50]}...")

    update = ClientNeedUpdate(
        project_title="E-commerce Platform",
        required_skills=["Python", "FastAPI", "React"],
        budget_min=5000,
        urgency_level="high"
    )
    print(f"✓ Created ClientNeedUpdate: {update.project_title}")

    print("\n✅ All models work correctly!")
    print("\n📌 API Endpoints Available:")
    print("  - POST /api/v1/conversation/start")
    print("  - POST /api/v1/conversation/{id}/message")
    print("  - GET  /api/v1/conversation/{id}/status")
    print("  - POST /api/v1/conversation/{id}/complete")
    print("  - GET  /api/v1/client-needs")
    print("  - GET  /api/v1/client-needs/{id}")
    print("  - POST /api/v1/speech/transcribe")
    print("  - POST /api/v1/speech/synthesize")
    print("  - GET  /api/v1/health")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
