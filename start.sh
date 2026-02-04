#!/bin/bash

# Start Agent UI

echo "Starting Agent UI..."

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    echo "Run: export ANTHROPIC_API_KEY=your-key"
    exit 1
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
echo "Agent UI running!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
