#!/usr/bin/env python3
"""
LM Studio Tools Integration for Task Manager
Exposes task management capabilities as tools that LM Studio can call
"""

import asyncio
import json
import sys
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class TaskManagerTools:
    """Exposes task management capabilities as LM Studio tools"""

    def __init__(self, server_path: str):
        self.server_path = server_path
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.available_tools = []

    async def connect_to_server(self):
        """Connect to the MCP task manager server"""
        try:
            server_params = StdioServerParameters(
                command="uv",
                args=["run", self.server_path],
                env=None,
            )

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )

            stdio, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(stdio, write)
            )

            await self.session.initialize()

            # Get available tools
            list_tools = await self.session.list_tools()
            self.available_tools = list_tools.tools

            print(f"✅ Connected to task manager server")
            print(f"📋 Available tools: {[tool.name for tool in self.available_tools]}")

            return True

        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return False

    async def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions in LM Studio format"""
        if not self.session:
            await self.connect_to_server()

        tools = []

        for tool in self.available_tools:
            # Convert MCP tool schema to LM Studio tool format
            tool_def = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }

            # Convert input schema if available
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = tool.inputSchema
                if isinstance(schema, dict):
                    if "properties" in schema:
                        tool_def["parameters"]["properties"] = schema["properties"]
                    if "required" in schema:
                        tool_def["parameters"]["required"] = schema["required"]

            tools.append(tool_def)

        return tools

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result"""
        if not self.session:
            await self.connect_to_server()

        try:
            # Execute the tool via MCP
            result = await self.session.call_tool(tool_name, arguments)

            # Format response for LM Studio
            if result.content:
                content = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        content.append(item.text)
                    else:
                        content.append(str(item))

                return {
                    "success": True,
                    "result": "\n".join(content)
                }
            else:
                return {
                    "success": True,
                    "result": "Tool executed successfully"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def cleanup(self):
        """Clean up connections"""
        await self.exit_stack.aclose()


# Example usage and test functions
async def test_tools():
    """Test the tools integration"""
    if len(sys.argv) < 2:
        print("Usage: python lm_studio_tools.py <server_path>")
        return

    server_path = sys.argv[1]
    tools = TaskManagerTools(server_path)

    try:
        # Connect and get tools
        await tools.connect_to_server()

        # Get tool definitions
        tool_defs = await tools.get_tool_definitions()
        print("\n🔧 Tool definitions for LM Studio:")
        print(json.dumps(tool_defs, indent=2))

        # Test a tool execution
        print("\n🧪 Testing add-task tool:")
        result = await tools.execute_tool("add-task", {
            "input": {
                "title": "Test Task from LM Studio",
                "description": "This task was created via LM Studio tools integration"
            }
        })
        print(f"Result: {result}")

        # Test listing tasks
        print("\n📋 Testing get-tasks:")
        result = await tools.execute_tool("get-tasks", {})
        print(f"Result: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await tools.cleanup()


if __name__ == "__main__":
    asyncio.run(test_tools())