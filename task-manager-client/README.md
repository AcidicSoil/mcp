<!-- @format -->

# Task Manager MCP Client with LM Studio Integration

A comprehensive Python MCP (Model Context Protocol) client that integrates with **LM Studio** for natural language task management. This client provides multiple ways to interact with the task manager:

1. **LM Studio Tools Integration** - Backend acceleration for LM Studio
2. **REST API Server** - HTTP endpoints for external applications
3. **Direct Python Client** - Programmatic access to task management

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   LM Studio     │    │  Task Manager    │    │   Task Manager      │
│   (Chat UI)     │◄──►│  API Server      │◄──►│   MCP Server        │
│                 │    │  (Port 8000)     │    │   (Stdio)           │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
         │                       │                        │
         │              ┌──────────────────┐              │
         └──────────────►│  LM Studio Tools │◄─────────────┘
                        │  Integration     │
                        └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **LM Studio** running with a model loaded
- **Task Manager Server** running (see `../task-manager-server/`)
- **Python 3.10+** with UV package manager

### 1. Start the Task Manager Server

```bash
cd ../task-manager-server
uv run task-manager.py
```

### 2. Start the API Server (for HTTP access)

```bash
cd task-manager-client
uv run api_server.py ../task-manager-server/task-manager.py
```

The API server will be available at:

- **API Base**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Interactive Docs**: http://localhost:8000/redoc

### 3. Test LM Studio Tools Integration

```bash
# Test the tools integration
uv run lm_studio_tools.py ../task-manager-server/task-manager.py
```

## 🛠️ Usage Examples

### REST API Usage

```bash
# Get all tasks
curl http://localhost:8000/tasks

# Add a new task
curl -X POST "http://localhost:8000/tasks?title=My%20Task&description=Task%20description"

# Get a specific task
curl http://localhost:8000/tasks/{task_id}

# Get available tool definitions
curl http://localhost:8000/tools

# Execute a tool directly
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "add-task",
    "arguments": {
      "input": {
        "title": "New Task",
        "description": "Task created via API"
      }
    }
  }'
```

### Python Integration

```python
from lm_studio_tools import TaskManagerTools

# Initialize tools
tools = TaskManagerTools("../task-manager-server/task-manager.py")
await tools.connect_to_server()

# Get tool definitions for LM Studio
tool_defs = await tools.get_tool_definitions()

# Execute tools
result = await tools.execute_tool("add-task", {
    "input": {
        "title": "Python Task",
        "description": "Created from Python"
    }
})
```

### LM Studio Integration

1. **Configure LM Studio** to use the task manager as a tool provider
2. **Chat with LM Studio** using natural language
3. **LM Studio automatically calls** task management tools when needed

Example conversation:

```
User: "Add a task to review the quarterly reports"
LM Studio: *calls add-task tool* "I've added a task titled 'Review quarterly reports' to your task list."

User: "What tasks do I have?"
LM Studio: *calls get-tasks tool* "You have 3 pending tasks: 1) Review quarterly reports, 2) Update documentation, 3) Schedule team meeting"
```

## 📋 Available Tools

The task manager exposes these tools to LM Studio:

- **`get-tasks`** - List all tasks
- **`add-task`** - Add a new task
- **`get-task`** - Get details for a specific task
- **`set-task-status`** - Update task status (pending, in_progress, completed)
- **`update-task`** - Update task details
- **`next-task`** - Get the next pending task

## 🔧 Configuration

### Environment Variables

- `MOCK_MODE=true` - Run in mock mode without LM Studio (for testing)

### API Server Configuration

The API server runs on `localhost:8000` by default. You can modify the host and port in `api_server.py`:

```python
uvicorn.run(
    "api_server:app",
    host="0.0.0.0",  # Change to bind to all interfaces
    port=8000,       # Change port if needed
    reload=False,
    log_level="info"
)
```

## 🧪 Testing

### Test Tools Integration

```bash
# Test with actual task manager server
uv run lm_studio_tools.py ../task-manager-server/task-manager.py

# Test in mock mode
MOCK_MODE=true uv run test_client.py
```

### Test API Server

```bash
# Start API server
uv run api_server.py ../task-manager-server/task-manager.py

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/tasks
curl -X POST "http://localhost:8000/tasks?title=Test&description=Test%20task"
```

## 📚 API Documentation

When the API server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 Troubleshooting

### Common Issues

1. **"Failed to connect to server"**

   - Ensure the task manager server is running
   - Check the server path is correct

2. **"LM Studio connection failed"**

   - Ensure LM Studio is running
   - Verify a model is loaded in LM Studio
   - Check LM Studio is accessible on default port

3. **"API server not starting"**
   - Check if port 8000 is already in use
   - Ensure all dependencies are installed: `uv sync`

### Debug Mode

Run with debug information:

```bash
# Enable debug logging
PYTHONPATH=. python -m uvicorn api_server:app --reload --log-level debug
```

## 🎯 Next Steps

1. **Configure LM Studio** to use this task manager as a tool provider
2. **Integrate with your workflow** by adding custom task types
3. **Extend the API** with additional endpoints for your specific needs
4. **Add authentication** if deploying in a multi-user environment

## 🤝 Integration with LM Studio

This client is designed to work as a **backend accelerator** for LM Studio, providing task management capabilities through natural language interaction. LM Studio can automatically discover and use these tools to help users manage their tasks more efficiently.

The integration supports both **direct tool calls** and **HTTP API access**, making it flexible for various deployment scenarios.

## Features

- 🤖 **Local LLM Integration**: Uses LM Studio for completely local AI processing
- 📋 **Task Management**: Full CRUD operations for tasks via natural language
- 🔗 **MCP Protocol**: Seamless integration with MCP servers
- 💬 **Interactive Chat**: Natural language interface for task management
- ⚡ **Real-time**: Instant task operations and updates

## Prerequisites

1. **Python 3.11+** with UV package manager
2. **LM Studio** running locally with a loaded model
3. **Task Manager Server** running (from ../task-manager-server/)

### Setting up LM Studio

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a compatible model (recommended: Qwen2.5-7B-Instruct for best tool calling)
3. Start the local server (default: http://localhost:1234)
4. Ensure the model supports function calling/tool use

## Installation

```bash
# Clone or navigate to the project
cd task-manager-client

# Install dependencies with UV
uv sync

# Copy environment template
cp .env.example .env

# Edit .env if needed (optional - defaults work for standard setup)
```

## Configuration

Create a `.env` file from the template:

```env
# LM Studio Configuration
LM_STUDIO_BASE_URL=http://localhost:1234
LM_STUDIO_API_KEY=lm-studio

# Task Manager Server Configuration
TASK_SERVER_PATH=../task-manager-server/task-manager.py

# Client Configuration
CLIENT_NAME=task-manager-client
CLIENT_VERSION=1.0.0
LOG_LEVEL=INFO
```

## Usage

### Basic Usage

```bash
# Start the client (make sure task-manager-server is running)
uv run client.py ../task-manager-server/task-manager.py
```

### Example Interactions

Once started, you can use natural language to manage tasks:

```
🎯 Query: Add a new task to review quarterly reports
🤖 Assistant: I've added a new task "Review quarterly reports" to your task list.

🎯 Query: Show me all my tasks
🤖 Assistant: Here are your current tasks:
1. Review quarterly reports (pending)
2. Update project documentation (pending)

🎯 Query: What's my next task?
🤖 Assistant: Your next pending task is "Review quarterly reports".

🎯 Query: Mark the quarterly reports task as completed
🤖 Assistant: I've marked "Review quarterly reports" as completed.
```

### Available Commands

The client automatically discovers and uses these tools from the server:

- `get-tasks`: List all tasks
- `add-task`: Add new tasks
- `set-task-status`: Update task status
- `get-task`: Get specific task details
- `next-task`: Get next pending task
- `update-task`: Update task information

## How It Works

1. **Connection**: Client connects to both LM Studio and the MCP task server
2. **Tool Discovery**: Automatically discovers available tools from the server
3. **Query Processing**: Sends user queries to LM Studio with tool information
4. **Tool Execution**: When LM Studio requests tool use, executes via MCP protocol
5. **Response**: Returns natural language response with task results

## Architecture

```
User Input → LM Studio (Local LLM) → Function Calling → MCP Client → Task Server
                      ↓
Natural Language Response ← Tool Results ← MCP Protocol ← Task Operations
```

## Troubleshooting

### Connection Issues

**LM Studio not connecting:**

- Ensure LM Studio is running on http://localhost:1234
- Check that a model is loaded and ready
- Verify the model supports function calling

**Task server not connecting:**

- Make sure task-manager-server is running
- Check the server path in the command line argument
- Ensure UV is installed and configured

### Model Issues

**Poor tool calling performance:**

- Use a model specifically trained for tool use (Qwen2.5-7B-Instruct recommended)
- Ensure model is loaded completely in LM Studio
- Check model temperature settings (0.7 works well)

### Common Error Messages

- `No models available in LM Studio`: Load a model in LM Studio first
- `Server script must be a .py file`: Provide correct path to task-manager.py
- `Failed to connect to task-manager-server`: Start the server first

## Development

### Project Structure

```
task-manager-client/
├── client.py           # Main client implementation
├── pyproject.toml      # UV project configuration
├── .env.example        # Environment template
├── README.md           # This file
└── requirements.txt    # Dependencies (auto-generated)
```

### Key Components

- **TaskManagerClient**: Main client class handling connections
- **LM Studio Integration**: Local LLM processing with function calling
- **MCP Protocol**: Server communication and tool execution
- **Interactive Interface**: Command-line chat interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both LM Studio and the task server
5. Submit a pull request

## License

This project is part of the MCP task management example suite.

## Related Projects

- [Task Manager Server](../task-manager-server/) - The MCP server this client connects to
- [LM Studio](https://lmstudio.ai/) - Local LLM platform
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification
