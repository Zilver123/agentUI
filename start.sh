#!/bin/bash

# Start AgentUI

echo "Starting AgentUI..."

# Load .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    echo "Set it in .env or run: export ANTHROPIC_API_KEY=your-key"
    exit 1
fi

# Create tools.py from sample if it doesn't exist
if [ ! -f backend/tools.py ]; then
    echo "Creating backend/tools.py from tools_sample.py..."
    cp backend/tools_sample.py backend/tools.py
fi

# Start backend
echo "Starting backend..."
cd backend
pip install -q -r requirements.txt
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 2

# Start frontend
echo "Starting frontend..."
cd frontend
npm install --silent
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "AgentUI running!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
