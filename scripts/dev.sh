#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
fi

# Default ports if not set in .env
FRONTEND_PORT=${FRONTEND_PORT:-3000}
API_PORT=${API_PORT:-8000}

# Check for required dependencies
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo "Error: $1 is required but not installed."
        echo "Please install dependencies from backend/requirements.txt:"
        echo "pip install -r backend/requirements.txt"
        exit 1
    fi
}

#check_dependency "uvicorn"
#check_dependency "npm"

# Start the backend
echo "Starting backend server on port $API_PORT..."
cd "$PROJECT_ROOT/backend" || exit 1
source venv/bin/activate 2>/dev/null || echo "No venv found, using system Python"
pip install -r requirements.txt
uvicorn app.main:app --reload --port $API_PORT --host $API_HOST &
BACKEND_PID=$!

# Start the frontend
echo "Starting frontend development server on port $FRONTEND_PORT..."
cd "$PROJECT_ROOT/frontend" || exit 1
PORT=$FRONTEND_PORT npm start &
FRONTEND_PID=$!

# Handle cleanup on script exit
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

trap cleanup INT TERM

# Keep script running and show logs
wait
