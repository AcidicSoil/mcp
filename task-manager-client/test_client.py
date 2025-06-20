#!/usr/bin/env python3
"""
Test script for Task Manager MCP Client
Demonstrates both mock mode (without LM Studio) and real mode (with LM Studio)
"""

import asyncio
import os
import sys
from client import TaskManagerClient


async def test_mock_mode():
    """Test client in mock mode without LM Studio"""
    print("=" * 60)
    print("🧪 TESTING MOCK MODE (No LM Studio required)")
    print("=" * 60)

    # Set mock mode
    os.environ["MOCK_MODE"] = "true"

    client = TaskManagerClient()

    try:
        # Initialize connections
        await client.setup_lm_studio()

        if len(sys.argv) >= 2:
            server_path = sys.argv[1]
            await client.connect_to_server(server_path)
        else:
            print("⚠️ No server path provided, skipping MCP server connection")
            print("Usage: python test_client.py <path_to_task_manager_server>")
            return

        # Test various queries
        test_queries = [
            "Hello!",
            "What can you do?",
            "Add a new task to review quarterly reports",
            "List all my tasks",
            "What's my next task?",
            "Mark task as completed",
            "Help me with my schedule"
        ]

        print("\n🔍 Testing queries:")
        for query in test_queries:
            print(f"\n👤 User: {query}")
            response = await client.process_query(query)
            print(f"🤖 Response: {response}")

    except Exception as e:
        print(f"❌ Mock mode test failed: {e}")
    finally:
        await client.cleanup()


async def test_real_mode():
    """Test client in real mode with LM Studio"""
    print("\n" + "=" * 60)
    print("🚀 TESTING REAL MODE (LM Studio required)")
    print("=" * 60)

    # Disable mock mode
    os.environ["MOCK_MODE"] = "false"

    client = TaskManagerClient()

    try:
        # Initialize connections
        await client.setup_lm_studio()

        if len(sys.argv) >= 2:
            server_path = sys.argv[1]
            await client.connect_to_server(server_path)
        else:
            print("⚠️ No server path provided, skipping MCP server connection")
            return

        # Test a simple query
        test_query = "Hello, can you help me add a task?"
        print(f"\n👤 User: {test_query}")
        response = await client.process_query(test_query)
        print(f"🤖 Response: {response}")

        print("\n✅ Real mode test completed successfully!")

    except Exception as e:
        print(f"❌ Real mode test failed: {e}")
        print("💡 Make sure LM Studio is running with a model loaded")
    finally:
        await client.cleanup()


async def main():
    """Main test function"""
    print("🧪 Task Manager MCP Client Test Suite")

    if len(sys.argv) < 2:
        print("\nUsage: python test_client.py <path_to_task_manager_server>")
        print("Example: python test_client.py ../task-manager-server/task-manager.py")
        print("\nThis will test both mock mode and real mode.")
        sys.exit(1)

    # Test mock mode first (always works)
    await test_mock_mode()

    # Ask user if they want to test real mode
    print("\n" + "=" * 60)
    try:
        choice = input("🤔 Do you want to test real mode with LM Studio? (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            await test_real_mode()
        else:
            print("⏭️ Skipping real mode test")
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")

    print("\n🎉 Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())