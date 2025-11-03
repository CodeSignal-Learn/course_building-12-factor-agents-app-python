#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down server...${NC}"
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    echo -e "${GREEN}Server stopped.${NC}"
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
echo -e "${BLUE}  12-Factor Agents - Starting Server${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Build frontend first
echo -e "${GREEN}Building frontend...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Build frontend (production bundle)
if [ ! -d "dist" ] || [ "package.json" -nt "dist" ]; then
    echo -e "${YELLOW}Building frontend assets...${NC}"
    npm run build
else
    echo -e "${YELLOW}Frontend build is up to date (dist/).${NC}"
fi

cd ..

# Start combined server (API + UI)
echo -e "${GREEN}Starting server on port 3000...${NC}"
cd backend
python3 -m uvicorn server.main:app --host 0.0.0.0 --port 3000 > ../server.log 2>&1 &
SERVER_PID=$!
cd ..

# Wait a moment for server to start
sleep 2

# Check if server started successfully
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}Error: Server failed to start${NC}"
    echo -e "${YELLOW}Check server.log for details${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}\n"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Server is running!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Application: ${GREEN}http://localhost:3000${NC}"
echo -e "API endpoints: ${GREEN}http://localhost:3000/agent/*${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop the server${NC}\n"
echo -e "${BLUE}Logs:${NC}"
echo -e "  Server: server.log\n"

# Wait for server process
wait $SERVER_PID

