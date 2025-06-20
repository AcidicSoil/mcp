# Quick Setup Guide - Codex HTTP Server with LM Studio

This guide helps you get the Codex HTTP Server running with LM Studio for local AI development.

## 🚀 Quick Start (5 minutes)

### Step 1: Install LM Studio

1. Download [LM Studio](https://lmstudio.ai/)
2. Install and launch it
3. Download a model (recommended: `qwen2.5-7b-instruct` or similar)

### Step 2: Start LM Studio Server

1. Open LM Studio
2. Go to **Local Server** tab
3. Load your downloaded model
4. Click **Start Server**
5. Ensure it shows: `Server running on http://localhost:1234`

### Step 3: Configure Codex

Create `~/.codex/config.toml`:

```toml
model = "qwen2.5-7b-instruct"  # Replace with your model name
model_provider = "ollama"
approval_policy = "never"

[model_providers.ollama]
name = "LM Studio"
base_url = "http://localhost:1234/v1"
wire_api = "chat"
```

### Step 4: Set Environment Variables

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export CODEX_MODEL="qwen2.5-7b-instruct"
export CODEX_PROVIDER="ollama"
export OLLAMA_BASE_URL="http://localhost:1234/v1"
export OPENAI_API_KEY="dummy-key"  # LM Studio doesn't need real key
```

Then reload: `source ~/.bashrc`

### Step 5: Build and Run Server

```bash
cd codex-rs/http-server
./start_server.sh
```

### Step 6: Test It

```bash
# Health check
python test_client.py --health-only

# Full test
python test_client.py --message "Write a hello world function in Python"
```

## ✅ Expected Output

When working correctly, you should see:

1. **Server startup**:

```
🔧 Configuration:
   Model: qwen2.5-7b-instruct
   Provider: ollama
   LM Studio URL: http://localhost:1234/v1
🌐 Starting server on http://127.0.0.1:8080
```

2. **Test response**:

```
✅ Health check passed: {'service': 'codex-http-server', 'status': 'healthy'}
✅ Connection established, streaming events:
📨 Event: {"event": "data", "data": {...}}
```

## 🔧 Alternative: Cloud Providers

Instead of LM Studio, you can use cloud providers:

### OpenAI

```bash
export OPENAI_API_KEY="sk-your-real-key"
export CODEX_PROVIDER="openai"
```

### Anthropic

```toml
# In ~/.codex/config.toml
model_provider = "anthropic"

[model_providers.anthropic]
name = "Anthropic"
base_url = "https://api.anthropic.com"
env_key = "ANTHROPIC_API_KEY"
wire_api = "chat"
```

## 🔧 Common Configuration Changes

⚠️ **Remember: Always restart the server after configuration changes!**

### Switch Models

```bash
# In LM Studio: Load different model
# Then update config:
export CODEX_MODEL="new-model-name"
# Or edit ~/.codex/config.toml

# RESTART SERVER:
# Stop with Ctrl+C, then:
./start_server.sh
```

### Switch to Cloud Provider

```bash
# For OpenAI:
export CODEX_PROVIDER="openai"
export OPENAI_API_KEY="sk-your-real-key"

# For Anthropic:
export CODEX_PROVIDER="anthropic"
export ANTHROPIC_API_KEY="your-anthropic-key"

# RESTART SERVER (required):
./start_server.sh
```

### Change LM Studio Port

```bash
# If LM Studio runs on different port:
export OLLAMA_BASE_URL="http://localhost:8080/v1"
```

### Debug Issues

```bash
# Enable detailed logging:
export RUST_LOG=debug
./start_server.sh
```

## 🆘 Need Help?

- Check the main [README.md](README.md) for detailed documentation
- See the **Troubleshooting** section for common issues
- See **How to Change Configuration** section for detailed config instructions

## 🎯 What's Next?

Once running, you can:

- Use the `/v1/responses` endpoint in your applications
- Integrate with OpenAI SDK, LangChain, or other tools
- Build web applications that use local AI
- Develop and test AI-powered features offline
