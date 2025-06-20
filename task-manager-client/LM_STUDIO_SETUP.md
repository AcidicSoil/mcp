<!-- @format -->

# LM Studio Integration Setup Guide

## 🎯 Overview

This guide shows you how to configure **LM Studio** to use our **Task Manager** as a backend service. The architecture works like this:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   LM Studio     │    │   Task Manager   │    │   Task Manager      │
│   (Chat UI)     │◄──►│   Middleware     │◄──►│   MCP Server        │
│   Port 1234     │    │   Port 1235      │    │   (Stdio)           │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## 🚀 Quick Start

### 1. Start the Task Manager Server

```bash
cd task-manager-server
uv run task-manager.py
```

_Keep this running in the background_

### 2. Start the OpenAI Middleware

```bash
cd task-manager-client
uv run openai_middleware.py ../task-manager-server/task-manager.py
```

_This creates an OpenAI-compatible API on port 1235_

### 3. Configure LM Studio

#### Option A: Use as External API (Recommended)

1. Open **LM Studio**
2. Go to **Local Server** tab
3. Click **Configure** or **Settings**
4. Add a new **External API Endpoint**:
   - **Name**: `Task Manager`
   - **Base URL**: `http://localhost:1235`
   - **API Key**: `not-required` (leave blank or any value)
   - **Model**: `task-manager`

#### Option B: Use in Chat Interface

1. In LM Studio's **Chat** interface
2. Click the **Model** dropdown
3. Select **Add External Model**
4. Enter:
   - **API Base**: `http://localhost:1235/v1`
   - **Model Name**: `task-manager`
   - **API Key**: (leave blank)

## 🧪 Testing the Integration

### Test 1: Basic Connection

```bash
curl http://localhost:1235/v1/models
```

Should return model information.

### Test 2: Add a Task

```bash
curl -X POST http://localhost:1235/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "task-manager",
    "messages": [
      {"role": "user", "content": "add task called Test Integration"}
    ]
  }'
```

### Test 3: List Tasks

```bash
curl -X POST http://localhost:1235/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "task-manager",
    "messages": [
      {"role": "user", "content": "show me my tasks"}
    ]
  }'
```

## 💬 Using in LM Studio Chat

Once configured, you can chat with LM Studio and it will automatically use the task manager for task-related requests:

**Example Conversations:**

👤 **User**: "Add a task to review the middleware code"
🤖 **LM Studio**: "✅ Created task: 'review the middleware code' (ID: abc123)"

👤 **User**: "What tasks do I have?"
🤖 **LM Studio**: "Here are your current tasks:
• Test Integration (TODO)
• review the middleware code (TODO)"

👤 **User**: "Mark the first task as done"
🤖 **LM Studio**: "✅ Updated task status to DONE"

## 🔧 Advanced Configuration

### Custom Port Configuration

If you need to change ports, edit the middleware:

```python
# In openai_middleware.py, change:
port=1235  # Change to your preferred port
```

### Adding More Tools

The middleware automatically discovers all MCP tools from the server. Current tools include:

- `add-task` - Create new tasks
- `get-tasks` - List all tasks
- `set-task-status` - Update task status
- `get-task` - Get specific task details
- `update-task` - Modify task details
- `next-task` - Get next task to work on

### Tool Detection Keywords

The middleware automatically detects when to use tools based on these keywords:

- **Add/Create**: "add", "create", "new" + "task"
- **List/Show**: "list", "show", "what" + "task"
- **Complete/Done**: "complete", "done", "finish" + "task"
- **Update**: "update", "change", "modify" + "task"

## 🐛 Troubleshooting

### Issue: "Connection refused"

- Make sure the task manager server is running
- Check that the middleware is running on port 1235
- Verify no firewall is blocking the ports

### Issue: "Model not found"

- Ensure you're using the correct model name: `task-manager`
- Check the base URL is correct: `http://localhost:1235/v1`

### Issue: "Tools not working"

- Verify the task manager server is responding
- Check the middleware logs for errors
- Test direct API calls using curl

### Issue: "LM Studio can't connect"

- Make sure LM Studio is configured to use the correct endpoint
- Try restarting both the middleware and LM Studio
- Check that ports 1234 (LM Studio) and 1235 (middleware) are available

## 📊 Architecture Details

### Request Flow

1. **User** types message in LM Studio
2. **LM Studio** sends OpenAI API request to middleware (port 1235)
3. **Middleware** analyzes message for task management keywords
4. **Middleware** calls appropriate MCP tool on task manager server
5. **Task Manager Server** executes the operation
6. **Middleware** formats response as OpenAI chat completion
7. **LM Studio** displays the result to user

### Supported Operations

- ✅ Natural language task creation
- ✅ Task listing and status checking
- ✅ Task status updates
- ✅ Task details retrieval
- ✅ Next task suggestions
- ✅ Task modifications
- 🔄 Smart keyword detection
- 🔄 Context-aware responses

## 🎉 Success!

Once everything is running, you'll have a fully integrated task management system where:

- **LM Studio** provides the chat interface
- **Our middleware** handles the translation
- **MCP server** manages the actual tasks
- **You** can manage tasks through natural conversation!

This creates a seamless experience where task management becomes as easy as chatting with an AI assistant.
