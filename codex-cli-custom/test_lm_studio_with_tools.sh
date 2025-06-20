#!/bin/bash

echo "Testing LM Studio API with tools (like Codex does)..."
echo "Model: osmosis-ai/osmosis-mcp-4b@q4_k_s"
echo "URL: http://localhost:1234/v1/chat/completions"
echo ""

# Test with the tools field like Codex sends
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "osmosis-ai/osmosis-mcp-4b@q4_k_s",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful AI assistant."
      },
      {
        "role": "user",
        "content": "Hello, this is a test message. Please respond with just: Test successful"
      }
    ],
    "stream": true,
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "shell",
          "description": "Runs a shell command, and returns its output.",
          "strict": false,
          "parameters": {
            "type": "object",
            "properties": {
              "command": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "workdir": {
                "type": "string"
              },
              "timeout": {
                "type": "number"
              }
            },
            "required": ["command"],
            "additionalProperties": false
          }
        }
      }
    ]
  }' | head -20

echo ""
echo ""
echo "If this fails but the simple test works, the issue is tools handling in LM Studio"