#!/bin/bash

echo "Testing LM Studio API directly..."
echo "Model: osmosis-ai/osmosis-mcp-4b@q4_k_s"
echo "URL: http://localhost:1234/v1/chat/completions"
echo ""

# Test the exact API call that Codex would make
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "osmosis-ai/osmosis-mcp-4b@q4_k_s",
    "messages": [
      {
        "role": "user",
        "content": "Hello, this is a test message. Please respond with just: Test successful"
      }
    ],
    "max_tokens": 50,
    "temperature": 0.1
  }' | jq .

echo ""
echo "If you see an error above, check:"
echo "1. LM Studio is running and shows 'Server running'"
echo "2. The model 'osmosis-ai/osmosis-mcp-4b@q4_k_s' is actively loaded (not just downloaded)"
echo "3. The server is actually listening on port 1234"