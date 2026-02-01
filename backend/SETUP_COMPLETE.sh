#!/bin/bash

echo "🚀 Installing full dependencies..."
source venv/bin/activate

# Install Azure and app packages
pip install openai azure-cognitiveservices-speech email-validator

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "📋 Next steps:"
echo "1. Make sure you've updated .env with your real credentials"
echo "2. Run: uvicorn client_need_service.main:app --reload --port 8000"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "🎉 Happy testing!"
