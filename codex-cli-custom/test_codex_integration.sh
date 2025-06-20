#!/bin/bash

echo "=== Codex CLI + Task Manager Integration Test ==="
echo "Timestamp: $(date)"
echo "Testing if Codex CLI uses our middleware with task management tools"
echo ""

# Set up environment
export OLLAMA_BASE_URL=http://localhost:1234
export OLLAMA_API_KEY=dummy-key

# Create log directory
mkdir -p logs
LOG_FILE="logs/codex_test_$(date +%Y%m%d_%H%M%S).log"

echo "=== Test Configuration ===" | tee $LOG_FILE
echo "OLLAMA_BASE_URL: $OLLAMA_BASE_URL" | tee -a $LOG_FILE
echo "OLLAMA_API_KEY: $OLLAMA_API_KEY" | tee -a $LOG_FILE
echo "Log file: $LOG_FILE" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

echo "=== Checking Services ===" | tee -a $LOG_FILE
echo "1. Testing middleware connection:" | tee -a $LOG_FILE
curl -s http://localhost:1234/v1/models | jq '.data[0].id' 2>/dev/null | tee -a $LOG_FILE || echo "Middleware not responding" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

echo "2. Testing task manager direct:" | tee -a $LOG_FILE
curl -s http://localhost:5000/tasks | jq '.' 2>/dev/null | tee -a $LOG_FILE || echo "Task manager not responding" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

echo "=== Testing Codex CLI ===" | tee -a $LOG_FILE

# Test 1: Simple task management request
echo "Test 1: Task Management Request" | tee -a $LOG_FILE
echo "Command: node dist/cli-dev.js -q \"Please use the get-tasks tool to show me current tasks\"" | tee -a $LOG_FILE
echo "Expected: Should call get-tasks tool through our middleware" | tee -a $LOG_FILE
echo "Output:" | tee -a $LOG_FILE

cd codex-cli
node dist/cli-dev.js -q "Please use the get-tasks tool to show me current tasks" 2>&1 | tee -a ../$LOG_FILE
echo "" | tee -a ../$LOG_FILE

# Test 2: Add task request
echo "Test 2: Add Task Request" | tee -a ../$LOG_FILE
echo "Command: node dist/cli-dev.js -q \"Add a new task called 'Test Codex Integration' with high priority using the add-task tool\"" | tee -a ../$LOG_FILE
echo "Expected: Should call add-task tool with our parameters" | tee -a ../$LOG_FILE
echo "Output:" | tee -a ../$LOG_FILE

node dist/cli-dev.js -q "Add a new task called 'Test Codex Integration' with high priority using the add-task tool" 2>&1 | tee -a ../$LOG_FILE
echo "" | tee -a ../$LOG_FILE

# Test 3: Verify task was added
echo "Test 3: Verification - Check tasks after addition" | tee -a ../$LOG_FILE
echo "Direct API call to verify task was added:" | tee -a ../$LOG_FILE
curl -s http://localhost:5000/tasks | jq '.' 2>/dev/null | tee -a ../$LOG_FILE
echo "" | tee -a ../$LOG_FILE

cd ..

echo "=== Test Complete ===" | tee -a $LOG_FILE
echo "Log file saved to: $LOG_FILE" | tee -a $LOG_FILE
echo "Check middleware.log for middleware activity logs" | tee -a $LOG_FILE

# Show summary
echo ""
echo "=== SUMMARY ==="
echo "Test log: $LOG_FILE"
echo "Middleware log: middleware.log"
echo "To analyze: Check if middleware.log shows incoming requests from Codex CLI"
echo "Expected: Should see POST requests to /v1/chat/completions with tool calls"