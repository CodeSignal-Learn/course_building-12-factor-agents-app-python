#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}Servers stopped.${NC}"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup SIGINT SIGTERM

# Check if we're in the project root
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY environment variable is not set${NC}"
    echo -e "${YELLOW}The backend may not work without it.${NC}\n"
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: node is not installed${NC}"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  12-Factor Agents - Starting Servers${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Start backend server
echo -e "${GREEN}Starting backend server on port 8000...${NC}"
cd backend
python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Error: Backend server failed to start${NC}"
    echo -e "${YELLOW}Check backend.log for details${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend server started (PID: $BACKEND_PID)${NC}\n"

# Start frontend dev server
echo -e "${GREEN}Starting frontend dev server on port 3000...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 2

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}Error: Frontend server failed to start${NC}"
    echo -e "${YELLOW}Check frontend.log for details${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Frontend dev server started (PID: $FRONTEND_PID)${NC}\n"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Servers are running!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Backend API:  ${GREEN}http://localhost:8000${NC}"
echo -e "Frontend UI:  ${GREEN}http://localhost:3000${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop both servers${NC}\n"
echo -e "${BLUE}Logs:${NC}"
echo -e "  Backend:  backend.log"
echo -e "  Frontend: frontend.log\n"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

