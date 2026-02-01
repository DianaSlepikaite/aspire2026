#!/bin/bash
# Start both Client Need Service and Employee Conversation Service

echo "======================================================================"
echo "Starting ASPIRE Services"
echo "======================================================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    source backend/venv/bin/activate
fi

# Stop any running instances (by process name and by port so ports are freed)
echo "Stopping any existing services..."
pkill -f "uvicorn client_need_service.main:app" 2>/dev/null
pkill -f "uvicorn employee_conversation_service.main:app" 2>/dev/null
# Free ports 8000 and 8001 in case something else is bound
for port in 8000 8001; do
  pid=$(lsof -ti:"$port" 2>/dev/null)
  if [[ -n "$pid" ]]; then
    echo "   Killing process on port $port (PID: $pid)"
    kill -9 $pid 2>/dev/null || true
  fi
done
echo "   Waiting for ports to be released..."
sleep 5

# Start Client Need Service (port 8000)
echo -e "\n📋 Starting Client Need Service on port 8000..."
cd backend
uvicorn client_need_service.main:app --host 0.0.0.0 --port 8000 &
CLIENT_PID=$!
echo "   PID: $CLIENT_PID"

sleep 3

# Start Employee Conversation Service (port 8001)
echo -e "\n👥 Starting Employee Conversation Service on port 8001..."
uvicorn employee_conversation_service.main:app --host 0.0.0.0 --port 8001 &
EMPLOYEE_PID=$!
echo "   PID: $EMPLOYEE_PID"

sleep 5

# Check health
echo -e "\n======================================================================"
echo "Health Checks"
echo "======================================================================"

CLIENT_HEALTH=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo "✅ Client Need Service: RUNNING"
    echo "   URL: http://localhost:8000/docs"
else
    echo "❌ Client Need Service: FAILED"
fi

EMPLOYEE_HEALTH=$(curl -s http://localhost:8001/api/v1/health 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo "✅ Employee Conversation Service: RUNNING"
    echo "   URL: http://localhost:8001/docs"
else
    echo "❌ Employee Conversation Service: FAILED"
fi

echo -e "\n======================================================================"
echo "Services Started"
echo "======================================================================"
echo "Client Need Service:        http://localhost:8000/docs"
echo "Employee Conversation Service: http://localhost:8001/docs"
echo ""
echo "To stop both services:"
echo "  pkill -f 'uvicorn.*main:app'"
echo "======================================================================"
