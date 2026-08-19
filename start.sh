#!/bin/bash

# LLM Council - Start script

echo "Starting LLM Council..."
echo ""

# Start backend
echo "Starting backend on http://localhost:8001..."
uv run python -m backend.main &
BACKEND_PID=$!

# Start MCP server for ChatGPT and other MCP clients
echo "Starting MCP server on http://localhost:8002/mcp..."
uv run --with "mcp>=1.27,<2" python -m backend.mcp_server &
MCP_PID=$!

# Wait a bit for backend to start
sleep 2

# Start frontend
echo "Starting frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✓ LLM Council is running!"
echo "  Backend:  http://localhost:8001"
echo "  Frontend: http://localhost:5173"
echo "  MCP:      http://localhost:8002/mcp"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $MCP_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
