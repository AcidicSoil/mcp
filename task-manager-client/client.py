import asyncio
import sys
import json
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import lmstudio as lms
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class TaskManagerClient:
    """MCP Client for Task Manager using LM Studio local LLM"""

    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.lm_model = None
        self.available_tools: List[Dict[str, Any]] = []
        self.client_name = "Task Manager MCP Client with LM Studio"
        # Add mock mode support
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"

        if self.mock_mode:
            print("🧪 Running in MOCK MODE - LM Studio not required")

        # Configuration
        self.client_version = os.getenv("CLIENT_VERSION", "1.0.0")

    async def connect_to_server(self, server_script_path: str):
        """Connect to the task-manager MCP server

        Args:
            server_script_path: Path to the server script (.py)
        """
        if not server_script_path.endswith(".py"):
            raise ValueError("Server script must be a .py file")

        # Set up server parameters
        server_params = StdioServerParameters(command="uv", args=["run", server_script_path], env=None)

        # Connect to server
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        # Initialize session
        await self.session.initialize()

        # Discover available tools
        response = await self.session.list_tools()
        self.available_tools = [
            {"name": tool.name, "description": tool.description, "input_schema": tool.inputSchema}
            for tool in response.tools
        ]

        print(f"✅ Connected to task-manager-server")
        print(f"📋 Available tools: {[tool['name'] for tool in self.available_tools]}")

    async def setup_lm_studio(self):
        """Initialize LM Studio model or mock mode"""
        if self.mock_mode:
            print("🤖 Mock LM Studio initialized")
            print("📝 Mock model ready for task management")
            return

        try:
            # Get the currently loaded model from LM Studio
            self.lm_model = lms.llm()

            # Test the model - complete() method doesn't accept max_tokens parameter
            test_response = self.lm_model.complete("Test")

            print(f"🤖 Connected to LM Studio")
            print(f"📝 Model ready for task management")

        except Exception as e:
            print(f"❌ Failed to connect to LM Studio: {e}")
            print("💡 Make sure LM Studio is running and a model is loaded")
            print("💡 Or run with MOCK_MODE=true for testing without LM Studio")
            raise

    async def process_query(self, query: str) -> str:
        """Process user query using LM Studio with tool calling or mock mode"""
        if self.mock_mode:
            return await self._process_query_mock(query)

        try:
            # Create a chat instance for conversation management
            chat = lms.Chat(self._create_system_message())
            chat.add_user_message(query)

            # Check if query might need tool usage based on keywords
            needs_tools = self._detect_tool_usage(query)

            if needs_tools:
                # For tool usage, we'll use a simplified approach
                # First get the LLM's intent
                intent_response = self.lm_model.respond(chat)

                # Parse the response to see if we need to execute tools
                tool_result = await self._try_execute_tools(query, intent_response)

                if tool_result:
                    # Add tool result to conversation and get final response
                    chat.add_assistant_response(intent_response)
                    chat.add_user_message(f"Tool execution result: {tool_result}")
                    final_response = self.lm_model.respond(chat)
                    return final_response
                else:
                    return intent_response
            else:
                # Direct response for non-tool queries
                return self.lm_model.respond(chat)

        except Exception as e:
            return f"❌ Error processing query: {str(e)}"

    async def _process_query_mock(self, query: str) -> str:
        """Mock query processing for testing without LM Studio"""
        query_lower = query.lower()

        # Check if query needs tool usage
        needs_tools = self._detect_tool_usage(query)

        if needs_tools:
            # Try to execute tools directly in mock mode
            tool_result = await self._try_execute_tools(query, "Mock LLM intent response")

            if tool_result:
                return f"🤖 Mock Assistant: I'll help you with that task. {tool_result}"
            else:
                return f"🤖 Mock Assistant: I understand you want to work with tasks. Here's what I would do: {query}"
        else:
            # Generate appropriate mock responses for non-tool queries
            if any(word in query_lower for word in ["hello", "hi", "hey"]):
                return "🤖 Mock Assistant: Hello! I'm here to help you manage your tasks. What would you like to do?"
            elif any(word in query_lower for word in ["help", "what can you do"]):
                return "🤖 Mock Assistant: I can help you add tasks, list your tasks, mark them as complete, and find your next task to work on."
            else:
                return f"🤖 Mock Assistant: I understand your request: '{query}'. In real mode, I would provide a more detailed response using the LM Studio model."

    def _create_system_message(self) -> str:
        """Create system message with tool information"""
        tools_info = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in self.available_tools])

        return f"""You are a helpful task management assistant. You have access to the following tools:

{tools_info}

When users ask about tasks, respond naturally but indicate what action you would take. For example:
- "I'll add that task for you" (for adding tasks)
- "Let me show you your tasks" (for listing tasks)
- "I'll mark that as completed" (for status updates)

Always be helpful and provide clear explanations of what you're doing."""

    def _detect_tool_usage(self, query: str) -> bool:
        """Simple heuristic to detect if query needs tool usage"""
        tool_keywords = [
            "add task",
            "create task",
            "new task",
            "list tasks",
            "show tasks",
            "my tasks",
            "all tasks",
            "next task",
            "what's next",
            "mark",
            "complete",
            "done",
            "status",
            "update task",
            "edit task",
            "change task",
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in tool_keywords)

    async def _try_execute_tools(self, query: str, intent_response: str) -> Optional[str]:
        """Try to execute appropriate tools based on query and intent"""
        query_lower = query.lower()

        try:
            # Add task
            if any(phrase in query_lower for phrase in ["add task", "create task", "new task"]):
                # Extract task title from query
                title = self._extract_task_title(query)
                if title:
                    result = await self.session.call_tool("add-task", {"title": title})
                    return f"✅ Added task: {title}"

            # List tasks
            elif any(phrase in query_lower for phrase in ["list tasks", "show tasks", "my tasks", "all tasks"]):
                result = await self.session.call_tool("get-tasks", {})
                tasks = result.content.get("tasks", [])
                if tasks:
                    task_list = "\n".join([f"• {task['title']} ({task['status']})" for task in tasks])
                    return f"📋 Your tasks:\n{task_list}"
                else:
                    return "📋 You have no tasks yet."

            # Next task
            elif any(phrase in query_lower for phrase in ["next task", "what's next"]):
                result = await self.session.call_tool("next-task", {})
                task = result.content.get("task")
                if task:
                    return f"⭐ Next task: {task['title']}"
                else:
                    return "✨ No pending tasks! You're all caught up."

            # Mark task complete (simplified - would need better parsing in production)
            elif any(phrase in query_lower for phrase in ["mark", "complete", "done"]):
                # For demo purposes, mark the first pending task as completed
                tasks_result = await self.session.call_tool("get-tasks", {})
                tasks = tasks_result.content.get("tasks", [])
                pending_tasks = [t for t in tasks if t.get("status") == "pending"]
                if pending_tasks:
                    task_id = pending_tasks[0]["id"]
                    await self.session.call_tool("set-task-status", {"task_id": task_id, "status": "completed"})
                    return f"✅ Marked '{pending_tasks[0]['title']}' as completed"
                else:
                    return "ℹ️ No pending tasks to mark as completed"

        except Exception as e:
            return f"⚠️ Tool execution error: {str(e)}"

        return None

    def _extract_task_title(self, query: str) -> Optional[str]:
        """Extract task title from query (simplified extraction)"""
        # Simple extraction - in production would use better NLP
        query_lower = query.lower()
        for phrase in ["add task", "create task", "new task"]:
            if phrase in query_lower:
                # Extract text after the phrase
                start_idx = query_lower.find(phrase) + len(phrase)
                title = query[start_idx:].strip()
                # Remove common prefixes
                for prefix in ["to ", "for ", "about ", ":"]:
                    if title.startswith(prefix):
                        title = title[len(prefix) :].strip()
                return title if title else None
        return None

    async def chat_loop(self):
        """Run interactive chat loop"""
        print(f"\n🚀 {self.client_name} Started!")
        print("💬 Type your task management queries or 'quit' to exit.")
        print("📝 Examples:")
        print("  - 'Add a new task to review quarterly reports'")
        print("  - 'Show me all my tasks'")
        print("  - 'What's my next task?'")
        print("  - 'Mark task as completed'")

        while True:
            try:
                query = input("\n🎯 Query: ").strip()

                if query.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if not query:
                    continue

                print("🤔 Processing...")
                response = await self.process_query(query)
                print(f"\n🤖 Assistant: {response}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
        # LM Studio model cleanup is handled automatically


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_task_manager_server>")
        print("Example: python client.py ../task-manager-server/task-manager.py")
        sys.exit(1)

    server_path = sys.argv[1]
    client = TaskManagerClient()

    try:
        # Initialize connections
        await client.setup_lm_studio()
        await client.connect_to_server(server_path)

        # Start interactive chat
        await client.chat_loop()

    except Exception as e:
        print(f"❌ Failed to start client: {e}")
        sys.exit(1)
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
