#!/usr/bin/env python3
"""
Simple test client for the Codex HTTP Server
"""

import requests
import json
import time
import sys
import argparse

def test_health_check(base_url):
    """Test the health check endpoint"""
    print("🩺 Testing health check endpoint...")
    try:
        response = requests.post(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_responses_endpoint(base_url, message):
    """Test the /v1/responses endpoint with SSE"""
    print(f"💬 Testing responses endpoint with message: '{message}'")

    payload = {
        "input": message,
        "store": True
    }

    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        }

        response = requests.post(
            f"{base_url}/v1/responses",
            json=payload,
            headers=headers,
            stream=True,
            timeout=30
        )

        if response.status_code == 200:
            print("✅ Connection established, streaming events:")
            print("-" * 50)

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        try:
                            data = json.loads(data_str)
                            print(f"📨 Event: {json.dumps(data, indent=2)}")
                        except json.JSONDecodeError:
                            print(f"📝 Raw data: {data_str}")
                    else:
                        print(f"📄 Line: {line_str}")

            print("-" * 50)
            print("✅ Stream completed successfully")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test the Codex HTTP Server')
    parser.add_argument('--url', default='http://127.0.0.1:8080',
                       help='Base URL of the server (default: http://127.0.0.1:8080)')
    parser.add_argument('--message', default='Hello, can you help me with a simple coding task?',
                       help='Test message to send')
    parser.add_argument('--health-only', action='store_true',
                       help='Only test the health endpoint')

    args = parser.parse_args()

    print(f"🔌 Testing Codex HTTP Server at {args.url}")
    print("=" * 60)

    # Test health check
    health_ok = test_health_check(args.url)

    if not health_ok:
        print("❌ Server health check failed, aborting further tests")
        sys.exit(1)

    if args.health_only:
        print("✅ Health check only mode - done!")
        sys.exit(0)

    print()

    # Test responses endpoint
    responses_ok = test_responses_endpoint(args.url, args.message)

    print()
    print("=" * 60)

    if health_ok and responses_ok:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
