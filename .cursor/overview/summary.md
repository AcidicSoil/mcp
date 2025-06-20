<!-- @format -->

# MCP Task Manager with LM Studio Integration

## Project Overview

This project creates a complete AI-powered task management system that integrates LM Studio with Model Context Protocol (MCP) through a custom middleware architecture. The system allows natural language interaction with task management through a local LLM while maintaining code awareness through a customized terminal agent.

## Current Architecture

```
Local Codebase → Custom Codex CLI → OpenAI Middleware → LM Studio → MCP Task Manager
```

**Components:**

1. **MCP Task Manager Server** (`task-manager-server/`) - Core task management with MCP protocol
2. **OpenAI Middleware** (`task-manager-client/`) - Translates OpenAI API calls to MCP protocol
3. **LM Studio Integration** - Local LLM that connects to middleware via OpenAI-compatible API
4. **Custom Codex CLI** - Terminal-based coding agent (to be customized from existing fork)

## Key Features

- **Local LLM Integration**: Uses LM Studio for AI interactions without external API dependencies
- **MCP Protocol**: Standards-compliant Model Context Protocol implementation
- **Code-Aware Task Management**: Terminal agent provides full codebase context to the AI
- **Natural Language Interface**: Interact with tasks using natural language through LM Studio
- **Middleware Architecture**: Clean separation between AI and task management logic

## Current Status

- ✅ MCP Task Manager Server - Fully functional
- ✅ OpenAI Middleware - Tested and working (localhost:1234)
- ✅ LM Studio Integration - Successfully making API calls
- 🚧 Custom Codex CLI - Ready for customization (user has existing fork)

## Next Steps

1. Customize Codex CLI fork to work with local middleware
2. Replace OpenAI API integration with local middleware calls
3. Enhance context collection for better code awareness
4. Add task management commands to CLI
5. Test end-to-end integration

## Technology Stack

- **Python**: Core language for MCP server and middleware
- **UV**: Package management and dependency handling
- **FastAPI**: Web framework for middleware API
- **MCP**: Model Context Protocol for AI-tool communication
- **LM Studio**: Local LLM hosting and inference
- **TypeScript/Node.js**: Codex CLI (to be customized)

## Architecture Benefits

- **Privacy**: Everything runs locally, no external API calls
- **Performance**: Direct local communication between components
- **Flexibility**: Modular architecture allows easy component swapping
- **Code Awareness**: Full project context available to AI
- **Task Integration**: Seamless task management within development workflow
