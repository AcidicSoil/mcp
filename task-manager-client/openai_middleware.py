#!/usr/bin/env python3
"""
OpenAI-Compatible Middleware for Task Manager MCP Server
Sits between LM Studio and our MCP server, translating OpenAI API calls to MCP protocol
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from lm_studio_tools import TaskManagerTools


# OpenAI API Models
class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: Dict[str, Any]


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "task-manager"


# Global task manager instance
task_manager: TaskManagerTools = None


# FastAPI app
app = FastAPI(
    title="Task Manager OpenAI Middleware",
    description="OpenAI-compatible API that bridges LM Studio to Task Manager MCP Server",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize task manager connection on startup"""
    global task_manager

    if len(sys.argv) < 2:
        print("❌ Error: Server path required")
        print("Usage: uvicorn openai_middleware:app --host 0.0.0.0 --port 1234 -- <server_path>")
        sys.exit(1)

    server_path = sys.argv[1]
    task_manager = TaskManagerTools(server_path)

    success = await task_manager.connect_to_server()
    if not success:
        print("❌ Failed to connect to task manager server")
        sys.exit(1)

    print("🚀 Task Manager OpenAI Middleware started!")
    print("📋 Available at: http://localhost:1234")
    print("🔧 LM Studio can now use this as OpenAI API endpoint")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    global task_manager
    if task_manager:
        await task_manager.cleanup()


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI API compatibility)"""
    return {
        "object": "list",
        "data": [
            ModelInfo(
                id="task-manager",
                created=int(datetime.now().timestamp()),
                owned_by="task-manager"
            ).dict()
        ]
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Handle chat completions with tool calling support"""
    global task_manager

    if not task_manager:
        raise HTTPException(status_code=500, detail="Task manager not initialized")

    try:
        # Get the last user message
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break

        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")

        # Check if this looks like a task management request
        task_keywords = ["task", "todo", "add", "create", "list", "show", "complete", "done", "update", "delete"]
        needs_tools = any(keyword in user_message.lower() for keyword in task_keywords)

        if needs_tools and request.tools:
            # This is a tool calling request
            return await handle_tool_request(request, user_message)
        else:
            # Regular chat completion
            return await handle_regular_chat(request, user_message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def handle_tool_request(request: ChatCompletionRequest, user_message: str):
    """Handle requests that need tool calling"""
    global task_manager

    # Analyze the user message to determine which tool to call
    message_lower = user_message.lower()

    tool_call = None
    tool_result = None

    if any(word in message_lower for word in ["add", "create", "new"]) and "task" in message_lower:
        # Extract task title and description from message
        title = extract_task_title(user_message)
        description = extract_task_description(user_message)

        tool_call = ToolCall(
            id=f"call_{uuid.uuid4().hex[:8]}",
            function={
                "name": "add-task",
                "arguments": json.dumps({
                    "input": {
                        "title": title,
                        "description": description
                    }
                })
            }
        )

        # Execute the tool
        tool_result = await task_manager.execute_tool("add-task", {
            "input": {
                "title": title,
                "description": description
            }
        })

    elif any(word in message_lower for word in ["list", "show", "what"]) and "task" in message_lower:
        tool_call = ToolCall(
            id=f"call_{uuid.uuid4().hex[:8]}",
            function={
                "name": "get-tasks",
                "arguments": "{}"
            }
        )

        # Execute the tool
        tool_result = await task_manager.execute_tool("get-tasks", {})

    # Generate response
    if tool_call and tool_result:
        if tool_result["success"]:
            # Parse the JSON result to make it more readable
            try:
                result_data = json.loads(tool_result["result"])
                if "tasks" in result_data:
                    tasks = result_data["tasks"]
                    if tasks:
                        task_list = "\n".join([f"• {task['title']} ({task['status']})" for task in tasks])
                        response_content = f"Here are your current tasks:\n{task_list}"
                    else:
                        response_content = "You don't have any tasks yet."
                elif "task" in result_data:
                    task = result_data["task"]
                    response_content = f"✅ Created task: '{task['title']}' (ID: {task['id']})"
                else:
                    response_content = "Task operation completed successfully."
            except:
                response_content = tool_result["result"]
        else:
            response_content = f"❌ Error: {tool_result.get('error', 'Unknown error')}"

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(datetime.now().timestamp()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content,
                    "tool_calls": [tool_call.dict()]
                },
                "finish_reason": "tool_calls"
            }],
            usage={
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(user_message.split()) + len(response_content.split())
            }
        ).dict()

    # Fallback to regular response
    return await handle_regular_chat(request, user_message)


async def handle_regular_chat(request: ChatCompletionRequest, user_message: str):
    """Handle regular chat completions without tools"""

    # Simple rule-based responses for task management
    message_lower = user_message.lower()

    if "task" in message_lower:
        if any(word in message_lower for word in ["add", "create", "new"]):
            response_content = "I can help you add tasks! What task would you like to create?"
        elif any(word in message_lower for word in ["list", "show", "what"]):
            response_content = "I can show you your tasks! Let me check what you have..."
        else:
            response_content = "I can help you manage your tasks. You can ask me to add new tasks or show your current tasks."
    else:
        response_content = "I'm a task management assistant. I can help you add, list, and manage your tasks. What would you like to do?"

    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        created=int(datetime.now().timestamp()),
        model=request.model,
        choices=[{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response_content
            },
            "finish_reason": "stop"
        }],
        usage={
            "prompt_tokens": len(user_message.split()),
            "completion_tokens": len(response_content.split()),
            "total_tokens": len(user_message.split()) + len(response_content.split())
        }
    ).dict()


def extract_task_title(message: str) -> str:
    """Extract task title from user message"""
    # Simple extraction - look for quoted text or text after "add task"
    message_lower = message.lower()

    # Look for quoted text
    if '"' in message:
        parts = message.split('"')
        if len(parts) >= 2:
            return parts[1]

    # Look for text after "add task" or similar
    for phrase in ["add task", "create task", "new task", "add a task"]:
        if phrase in message_lower:
            idx = message_lower.find(phrase)
            after_phrase = message[idx + len(phrase):].strip()
            if after_phrase:
                # Take first sentence or up to punctuation
                for punct in ['.', '!', '?', '\n']:
                    if punct in after_phrase:
                        after_phrase = after_phrase.split(punct)[0]
                return after_phrase.strip()

    # Fallback - use the whole message (cleaned)
    return message.replace("add task", "").replace("create task", "").strip()


def extract_task_description(message: str) -> str:
    """Extract task description from user message"""
    # For now, return empty description
    # Could be enhanced to extract more detailed descriptions
    return ""


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Task Manager OpenAI Middleware",
        "version": "1.0.0",
        "description": "OpenAI-compatible API for Task Manager MCP Server",
        "endpoints": {
            "models": "/v1/models",
            "chat": "/v1/chat/completions"
        }
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python openai_middleware.py <server_path>")
        sys.exit(1)

    # Run on port 1235 (since LM Studio is using 1234)
    uvicorn.run(
        "openai_middleware:app",
        host="0.0.0.0",
        port=1235,
        reload=False,
        log_level="info"
    )