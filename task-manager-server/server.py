from typing import List, Optional, Dict
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from tasks_db import TaskDB

db = TaskDB()

# Schemas
class Task(BaseModel):
    id: str
    title: str
    description: str
    status: str

class AddTaskInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = ""

class SetTaskStatusInput(BaseModel):
    task_id: str
    status: str

class UpdateTaskInput(BaseModel):
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None

class GetTaskInput(BaseModel):
    task_id: str

# MCP Server
mcp = FastMCP("task-mcp-server")

@mcp.tool("get-tasks", description="List all tasks.")
async def get_tasks() -> Dict[str, List[Task]]:
    return {"tasks": [Task(**t) for t in db.list_tasks()]}

@mcp.tool("add-task", description="Add a new task.")
async def add_task(input: AddTaskInput) -> Dict[str, Task]:
    task = db.add_task(input.title, input.description or "")
    return {"task": Task(**task)}

@mcp.tool("set-task-status", description="Set a task's status.")
async def set_task_status(input: SetTaskStatusInput) -> Dict[str, bool]:
    ok = db.set_status(input.task_id, input.status)
    return {"success": ok}

@mcp.tool("get-task", description="Get details for a specific task.")
async def get_task(input: GetTaskInput) -> Dict[str, Optional[Task]]:
    t = db.get_task(input.task_id)
    return {"task": Task(**t) if t else None}

@mcp.tool("next-task", description="Get the next pending task.")
async def next_task() -> Dict[str, Optional[Task]]:
    t = db.next_task()
    return {"task": Task(**t) if t else None}

@mcp.tool("update-task", description="Update task details.")
async def update_task(input: UpdateTaskInput) -> Dict[str, Optional[Task]]:
    updated = db.update_task(input.task_id, input.title, input.description)
    return {"task": Task(**updated) if updated else None}

# Entrypoint
if __name__ == "__main__":
    mcp.run(transport='stdio')