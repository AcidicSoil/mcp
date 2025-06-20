@echo off
echo === Codex CLI + Task Manager Integration Test ===
echo Timestamp: %date% %time%
echo Testing if Codex CLI uses our middleware with task management tools
echo.

rem Set up environment
set OLLAMA_BASE_URL=http://localhost:1234
set OLLAMA_API_KEY=dummy-key

rem Create log directory
if not exist logs mkdir logs
set LOG_FILE=logs\codex_test_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

echo === Test Configuration === > %LOG_FILE%
echo OLLAMA_BASE_URL: %OLLAMA_BASE_URL% >> %LOG_FILE%
echo OLLAMA_API_KEY: %OLLAMA_API_KEY% >> %LOG_FILE%
echo Log file: %LOG_FILE% >> %LOG_FILE%
echo. >> %LOG_FILE%

echo === Checking Services === >> %LOG_FILE%
echo 1. Testing middleware connection: >> %LOG_FILE%
curl -s http://localhost:1234/v1/models >> %LOG_FILE% 2>&1
echo. >> %LOG_FILE%

echo 2. Testing task manager direct: >> %LOG_FILE%
curl -s http://localhost:5000/tasks >> %LOG_FILE% 2>&1
echo. >> %LOG_FILE%

echo === Testing Codex CLI === >> %LOG_FILE%

rem Test 1: Simple task management request
echo Test 1: Task Management Request >> %LOG_FILE%
echo Command: node dist/cli-dev.js -q "Please use the get-tasks tool to show me current tasks" >> %LOG_FILE%
echo Expected: Should call get-tasks tool through our middleware >> %LOG_FILE%
echo Output: >> %LOG_FILE%

cd codex-cli
node dist/cli-dev.js -q "Please use the get-tasks tool to show me current tasks" >> ..\%LOG_FILE% 2>&1
echo. >> ..\%LOG_FILE%

rem Test 2: Add task request
echo Test 2: Add Task Request >> ..\%LOG_FILE%
echo Command: node dist/cli-dev.js -q "Add a new task called 'Test Codex Integration' with high priority using the add-task tool" >> ..\%LOG_FILE%
echo Expected: Should call add-task tool with our parameters >> ..\%LOG_FILE%
echo Output: >> ..\%LOG_FILE%

node dist/cli-dev.js -q "Add a new task called 'Test Codex Integration' with high priority using the add-task tool" >> ..\%LOG_FILE% 2>&1
echo. >> ..\%LOG_FILE%

rem Test 3: Verify task was added
echo Test 3: Verification - Check tasks after addition >> ..\%LOG_FILE%
echo Direct API call to verify task was added: >> ..\%LOG_FILE%
curl -s http://localhost:5000/tasks >> ..\%LOG_FILE% 2>&1
echo. >> ..\%LOG_FILE%

cd ..

echo === Test Complete === >> %LOG_FILE%
echo Log file saved to: %LOG_FILE% >> %LOG_FILE%
echo Check middleware.log for middleware activity logs >> %LOG_FILE%

rem Show summary
echo.
echo === SUMMARY ===
echo Test log: %LOG_FILE%
echo Middleware log: middleware.log
echo To analyze: Check if middleware.log shows incoming requests from Codex CLI
echo Expected: Should see POST requests to /v1/chat/completions with tool calls