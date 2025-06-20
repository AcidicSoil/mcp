# Codex CLI + Task Manager Integration Testing Guide

## Overview

This guide shows how to test the integrated Codex CLI with our custom task manager middleware that provides MCP (Model Context Protocol) tools.

## Architecture

```
Codex CLI → Middleware (localhost:1234) → Task Manager Server → MCP Tools
```

## Prerequisites

✅ Task manager server running on port 5000
✅ OpenAI middleware running on port 1234
✅ Docker container with Codex CLI running
✅ Configuration files set up
⚠️ **LM Studio must have a model loaded!**

## IMPORTANT: LM Studio Setup

### Before Testing - Load Model in LM Studio

1. Open LM Studio application
2. Go to "Developer" tab
3. **Load the osmosis model**: `osmosis-ai/osmosis-mcp-4b@q4_k_s`
4. Verify the model is loaded (should show "Model loaded" status)
5. Ensure LM Studio server is running on port 1234

### Verify Model is Loaded

```bash
curl http://localhost:1234/v1/models | jq '.data[].id'
# Should show available models including osmosis-ai/osmosis-mcp-4b@q4_k_s
```

## Testing in Docker Container

### 1. Access the Container

```bash
docker exec -it $(docker ps -q --filter "ancestor=codex-sandbox") bash
```

### 2. Navigate to Codex CLI Directory

```bash
cd /workspace/codex-cli-custom/codex-cli
```

### 3. Load Environment Variables

```bash
source ../.env
export OLLAMA_BASE_URL=http://host.docker.internal:1234
export OLLAMA_API_KEY=dummy-key
```

### 4. Build Codex CLI (Development Mode)

```bash
npm run build:dev
```

### 5. Test Basic Functionality

```bash
# Simple test - should connect to our middleware
node dist/cli-dev.js --help

# Test with a simple task
echo "console.log('Hello from Codex');" > test.js
node dist/cli-dev.js "Add a comment to this JavaScript file explaining what it does"
```

### 6. Test Task Manager Integration

```bash
# Test task management capabilities
node dist/cli-dev.js "Please use the available tools to show me the current tasks"

# Test adding a task
node dist/cli-dev.js "Add a new task: 'Test Codex CLI integration' with high priority"

# Test task completion
node dist/cli-dev.js "Mark the first task as completed using the available tools"
```

## Testing on Host (Alternative Method)

If Docker commands are problematic, you can test directly on the host:

### 1. Navigate to Codex CLI Directory

```bash
cd codex-cli-custom/codex-cli
```

### 2. Set Environment Variables (Windows)

```cmd
set OLLAMA_BASE_URL=http://localhost:1234
set OLLAMA_API_KEY=dummy-key
```

### 3. Update Config for Host Testing

```bash
cat > ../.codex/config.json << 'EOF'
{
  "model": "osmosis-ai/osmosis-mcp-4b@q4_k_s",
  "provider": "ollama",
  "approvalMode": "suggest",
  "fullAutoErrorMode": "ignore-and-continue"
}
EOF
```

### 4. Build and Test

```cmd
rem Build the project
set NODE_ENV=development && node build.mjs --dev

rem Test basic functionality
set OLLAMA_BASE_URL=http://localhost:1234 && set OLLAMA_API_KEY=dummy-key && node dist/cli-dev.js --help

rem Test with a simple file
echo console.log('Hello from Codex'); > test.js
set OLLAMA_BASE_URL=http://localhost:1234 && set OLLAMA_API_KEY=dummy-key && node dist/cli-dev.js -q "Add a comment to test.js"
```

## Configuration Details

### Current Configuration

- **Model**: `osmosis-ai/osmosis-mcp-4b@q4_k_s`
- **Provider**: `ollama`
- **Base URL**: `http://host.docker.internal:1234` (container) or `http://localhost:1234` (host)
- **Approval Mode**: `suggest` for interactive testing, `full-auto` for automated testing

### Available MCP Tools

The middleware provides these task management tools:

- `get-tasks` - Retrieve current tasks
- `add-task` - Add a new task
- `update-task` - Update existing task
- `delete-task` - Delete a task
- `complete-task` - Mark task as completed

## Troubleshooting

### Common Issues

1. **Model Not Found (404 Error)**

   ```bash
   # Check if LM Studio has a model loaded
   curl http://localhost:1234/v1/models
   # If empty or no osmosis model, load it in LM Studio Developer tab
   ```

2. **Connection Refused**

   ```bash
   # Check if middleware is running
   curl http://localhost:1234/v1/models
   ```

3. **Tool Calls Not Working**
   ```bash
   # Test tools directly
   curl -X POST http://localhost:1234/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "osmosis-ai/osmosis-mcp-4b@q4_k_s",
       "messages": [{"role": "user", "content": "Please use get-tasks tool"}],
       "tools": [{"type": "function", "function": {"name": "get-tasks"}}]
     }'
   ```

### Debug Commands

```bash
# Check services status
ps aux | grep -E "(task-manager|middleware)"

# Check ports
netstat -tlnp | grep -E "(1234|5000)"

# View middleware logs
# (Check terminal where middleware is running)

# Test task manager directly
curl http://localhost:5000/tasks
```

## Expected Behavior

### Successful Integration Signs

1. ✅ Codex CLI connects without errors
2. ✅ Model responds to simple prompts
3. ✅ Tool calls are executed (get-tasks, add-task, etc.)
4. ✅ Task manager state updates correctly
5. ✅ Responses include tool execution results

### Sample Successful Interaction

```
$ node dist/cli-dev.js "Show me current tasks and add a new one"

[Codex should:]
1. Call get-tasks tool
2. Display current tasks
3. Call add-task tool
4. Confirm task addition
5. Show updated task list
```

## Quick Test Results

### Host Testing Status

✅ **Services Running**: Task manager (port 5000) + Middleware (port 1234)
✅ **Codex CLI Built**: Successfully compiled in development mode
✅ **Configuration**: Ollama provider with osmosis model
⚠️ **Model Loading**: Requires active model in LM Studio

### Current Issue

- **Error**: `404 No models loaded`
- **Solution**: Load `osmosis-ai/osmosis-mcp-4b@q4_k_s` in LM Studio Developer tab
- **Verification**: `curl http://localhost:1234/v1/models` should show loaded models

## Next Steps After Successful Testing

1. **Customize Codex CLI** - Add task-specific prompts and behaviors
2. **Create Task Templates** - Pre-defined task management workflows
3. **Add Project Integration** - Connect to project-specific task contexts
4. **Build Production Version** - Create optimized build for deployment

## Notes

- **Critical**: Always ensure LM Studio has a model loaded before testing
- Keep this guide updated as configuration changes
- Test both container and host environments
- Document any custom modifications made to Codex CLI
- Save successful test commands for future reference
