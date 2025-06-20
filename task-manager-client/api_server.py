#!/usr/bin/env python3
"""
HTTP API Server for Task Manager Tools
Exposes task management capabilities via REST API for LM Studio integration
"""

import asyncio
import json
import sys
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from lm_studio_tools import TaskManagerTools


# Pydantic models for API
class ToolExecutionRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


class ToolExecutionResponse(BaseModel):
    success: bool
    result: Any = None
    error: str = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


# Global task manager instance
task_manager: TaskManagerTools = None


# FastAPI app
app = FastAPI(
    title="Task Manager API",
    description="HTTP API for Task Manager MCP Tools - LM Studio Integration",
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
        print("Usage: uvicorn api_server:app --reload -- <server_path>")
        sys.exit(1)

    server_path = sys.argv[1]
    task_manager = TaskManagerTools(server_path)

    success = await task_manager.connect_to_server()
    if not success:
        print("❌ Failed to connect to task manager server")
        sys.exit(1)

    print("🚀 Task Manager API Server started!")
    print("📋 Available at: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    global task_manager
    if task_manager:
        await task_manager.cleanup()


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "Task Manager API",
        "version": "1.0.0",
        "description": "HTTP API for Task Manager MCP Tools - LM Studio Integration",
        "endpoints": {
            "tools": "/tools",
            "execute": "/execute",
            "docs": "/docs"
        }
    }


@app.get("/tools", response_model=List[ToolDefinition])
async def get_tools():
    """Get available tool definitions"""
    global task_manager

    if not task_manager:
        raise HTTPException(status_code=500, detail="Task manager not initialized")

    try:
        tools = await task_manager.get_tool_definitions()
        return tools
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")


@app.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """Execute a tool with given arguments"""
    global task_manager

    if not task_manager:
        raise HTTPException(status_code=500, detail="Task manager not initialized")

    try:
        result = await task_manager.execute_tool(request.tool_name, request.arguments)

        if result["success"]:
            return ToolExecutionResponse(
                success=True,
                result=result["result"]
            )
        else:
            return ToolExecutionResponse(
                success=False,
                error=result.get("error", "Unknown error")
            )

    except Exception as e:
        return ToolExecutionResponse(
            success=False,
            error=str(e)
        )


# Convenience endpoints for common operations
@app.get("/tasks")
async def get_tasks():
    """Get all tasks (convenience endpoint)"""
    global task_manager

    if not task_manager:
        raise HTTPException(status_code=500, detail="Task manager not initialized")

    try:
        result = await task_manager.execute_tool("get-tasks", {})
        if result["success"]:
            # Parse JSON result
            tasks_data = json.loads(result["result"])
            return tasks_data
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get tasks"))
    except json.JSONDecodeError:
        # If result is not JSON, return as-is
        return {"result": result["result"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks")
async def add_task(title: str, description: str = ""):
    """Add a new task (convenience endpoint)"""
    global task_manager

    if not task_manager:
        raise HTTPException(status_code=500, detail="Task manager not initialized")

    try:
        result = await task_manager.execute_tool("add-task", {
            "input": {
                "title": title,
                "description": description
            }
        })

        if result["success"]:
            # Parse JSON result
            task_data = json.loads(result["result"])
            return task_data
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to add task"))
    except json.JSONDecodeError:
        # If result is not JSON, return as-is
        return {"result": result["result"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task (convenience endpoint)"""
    global task_manager

    if not task_manager:
        raise HTTPException(status_code=500, detail="Task manager not initialized")

    try:
        result = await task_manager.execute_tool("get-task", {
            "input": {
                "task_id": task_id
            }
        })

        if result["success"]:
            # Parse JSON result
            task_data = json.loads(result["result"])
            return task_data
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Task not found"))
    except json.JSONDecodeError:
        # If result is not JSON, return as-is
        return {"result": result["result"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python api_server.py <server_path>")
        sys.exit(1)

    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )