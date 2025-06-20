# Codex HTTP Server

An Axum-based HTTP server that provides REST API endpoints for interacting with the Codex core functionality.

## Overview

This HTTP server exposes the Codex agent functionality through REST API endpoints, allowing external applications to interact with Codex programmatically. It provides OpenAI-compatible `/v1/responses` endpoints that can be used with MCP SDK, OpenAI SDK, LangChain, and other compatible tools.

**🚀 New to setup?** See [SETUP.md](SETUP.md) for a quick 5-minute guide to get running with LM Studio.

## API Endpoints

### POST /v1/responses

Submit user input and receive a streaming response from the Codex agent using Server-Sent Events (SSE).

**Request Body:**

```json
{
  "input": "Your message to the agent",
  "previous_response_id": "optional-previous-response-id",
  "instructions": "Optional instructions for the agent",
  "store": true
}
```

**Response:**
Server-Sent Events (SSE) stream with JSON data containing agent events and responses.

### POST /health

Health check endpoint that returns the server status.

**Response:**

```json
{
  "status": "healthy",
  "service": "codex-http-server"
}
```

## Usage

### Prerequisites

1. **Codex Environment**: Ensure you have the Codex environment properly configured
2. **LM Studio Setup** (recommended for local development):
   - Install and run [LM Studio](https://lmstudio.ai/)
   - Load a model (e.g., `qwen2.5-7b-instruct`)
   - Enable the local server on port 1234
   - Or set up API keys for cloud providers (e.g., `OPENAI_API_KEY` for OpenAI)
3. **Configuration**: The server automatically loads from:
   - `~/.codex/config.toml` (Rust configuration)
   - Environment variables from your shell (`.bashrc`, `.env`)
   - Command-line overrides

### Running the Server

#### Option 1: Using the startup script (recommended)

```bash
cd codex-rs/http-server
./start_server.sh
```

#### Option 2: Using cargo directly

```bash
cargo run -p codex-http-server
```

The server will start on `http://127.0.0.1:8080` and display:

```
Codex HTTP Server listening on 127.0.0.1:8080
Endpoints:
  POST /v1/responses - OpenAI-compatible responses endpoint
  POST /health - Health check
```

The startup script will also show your current configuration:

```
🔧 Configuration:
   Model: [dynamically read from ~/.codex/config.toml or environment]
   Provider: [dynamically read from ~/.codex/config.toml or environment]
   Base URL: [dynamically read from ~/.codex/config.toml or environment]
   Approval Policy: [dynamically read from ~/.codex/config.toml or environment]
   Config File: ~/.codex/config.toml (checked for existence)
```

### Example Requests

#### Basic Query

```bash
curl -X POST http://127.0.0.1:8080/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, can you help me with a coding task?"}'
```

#### With Instructions

```bash
curl -X POST http://127.0.0.1:8080/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a Python function to calculate fibonacci numbers",
    "instructions": "Use recursive approach and add comments",
    "store": true
  }'
```

#### Health Check

```bash
curl -X POST http://127.0.0.1:8080/health
```

### Testing the Server

A Python test client is provided to verify the server is working correctly:

```bash
# Test health check only
python3 codex-rs/http-server/test_client.py --health-only

# Test both health check and responses endpoint
python3 codex-rs/http-server/test_client.py

# Test with custom message
python3 codex-rs/http-server/test_client.py --message "Create a hello world function in Python"

# Test with custom server URL
python3 codex-rs/http-server/test_client.py --url http://localhost:8080
```

## Troubleshooting

### Common Issues

#### 1. "Invalid API key provided: 1234" Error

**Problem**: Server is trying to connect to OpenAI instead of LM Studio
**Solution**:

- Ensure `~/.codex/config.toml` exists with proper `model_provider = "ollama"`
- Check environment variables: `echo $CODEX_PROVIDER` should show "ollama"
- Verify LM Studio is running on port 1234
- **⚠️ RESTART THE SERVER** after making config changes

#### 2. Connection Refused to localhost:1234

**Problem**: LM Studio server is not running
**Solution**:

- Start LM Studio
- Go to Local Server tab
- Click "Start Server"
- Ensure port is set to 1234

#### 3. Server Won't Start

**Problem**: Configuration or build issues
**Solution**:

```bash
# Check configuration
./start_server.sh  # Shows current config

# Rebuild if needed
cargo clean
cargo build -p codex-http-server

# Check logs
RUST_LOG=debug cargo run -p codex-http-server
```

#### 4. Model Not Found

**Problem**: Model name mismatch between config and LM Studio
**Solution**:

- Check loaded model in LM Studio
- Update `model = "actual-model-name"` in `~/.codex/config.toml`
- Or set `export CODEX_MODEL="actual-model-name"`

### Debug Mode

Enable detailed logging:

```bash
export RUST_LOG=debug
cargo run -p codex-http-server
```

## Configuration

The server dynamically reads configuration from multiple sources with the following precedence (highest to lowest):

1. **Environment Variables** (highest precedence)

   - `CODEX_MODEL` - Override the model name
   - `CODEX_PROVIDER` - Override the model provider
   - `CODEX_APPROVAL_POLICY` - Override approval policy
   - `OLLAMA_BASE_URL` - Override the base URL for ollama/LM Studio

2. **Configuration File** (`~/.codex/config.toml`)

   - Automatically loaded by the Rust core
   - Contains model, provider, and other settings

3. **Built-in Defaults** (lowest precedence)

### Dynamic Configuration Display

The startup script (`./start_server.sh`) will dynamically read and display your current configuration:

- Reads from `~/.codex/config.toml` if it exists
- Shows environment variable overrides
- Indicates missing configuration values
- Checks if config file exists

The server supports multiple configuration sources with the following precedence (highest to lowest):

1. **Command-line arguments** (not implemented yet, but planned)
2. **Environment variables**: `CODEX_MODEL`, `CODEX_PROVIDER`, `OLLAMA_BASE_URL`, etc.
3. **Rust config file**: `~/.codex/config.toml`
4. **Built-in defaults**

### Configuration Files

#### `~/.codex/config.toml` (Rust Configuration)

```toml
# Model and provider settings
model = "qwen2.5-7b-instruct"
model_provider = "ollama"
approval_policy = "never"

# Custom provider definitions
[model_providers.ollama]
name = "LM Studio (Ollama-compatible)"
base_url = "http://localhost:1234/v1"
wire_api = "chat"
```

#### Environment Variables (from `.bashrc` or `.env`)

```bash
export CODEX_MODEL="qwen2.5-7b-instruct"
export CODEX_PROVIDER="ollama"
export OLLAMA_BASE_URL="http://localhost:1234/v1"
export OPENAI_API_KEY="1234"  # Dummy key for LM Studio
```

### Supported Providers

The server supports multiple AI providers:

- **LM Studio** (recommended for local development)

  - Base URL: `http://localhost:1234/v1`
  - No API key required
  - Compatible with Ollama wire protocol

- **OpenAI** (cloud)

  - Requires `OPENAI_API_KEY`
  - Uses Responses API format

- **Ollama** (local)

  - Base URL: `http://localhost:11434/v1`
  - No API key required

- **Other providers**: Anthropic, Gemini, DeepSeek, etc.

### How to Change Configuration

#### Method 1: Environment Variables (Temporary)

```bash
# Change model for current session
export CODEX_MODEL="different-model-name"
export CODEX_PROVIDER="openai"
export OPENAI_API_KEY="sk-your-real-key"

# IMPORTANT: Restart server to apply changes
# Stop current server (Ctrl+C), then:
./start_server.sh
```

#### Method 2: Update ~/.codex/config.toml (Permanent)

```bash
# Edit the config file
nano ~/.codex/config.toml

# Example changes:
model = "gpt-4o"                    # Change model
model_provider = "openai"           # Switch to OpenAI
approval_policy = "unless-allow-listed"  # Change approval mode

# Add new provider
[model_providers.anthropic]
name = "Anthropic Claude"
base_url = "https://api.anthropic.com/v1"
env_key = "ANTHROPIC_API_KEY"
wire_api = "chat"
```

#### Method 3: Update Shell Configuration (Persistent)

```bash
# Edit your shell config
nano ~/.bashrc  # or ~/.zshrc

# Add or modify exports
export CODEX_MODEL="new-model"
export CODEX_PROVIDER="new-provider"

# Reload shell config
source ~/.bashrc
```

#### Common Configuration Changes

**Switch from LM Studio to OpenAI:**

```bash
# Set environment variables
export CODEX_PROVIDER="openai"
export OPENAI_API_KEY="sk-your-actual-key"

# Or update config.toml
echo 'model_provider = "openai"' >> ~/.codex/config.toml
```

**Change to different local model:**

```bash
# Update model name to match what's loaded in LM Studio
export CODEX_MODEL="llama-3.2-3b-instruct"

# Or in config.toml
sed -i 's/model = .*/model = "llama-3.2-3b-instruct"/' ~/.codex/config.toml
```

**Add custom provider:**

```bash
# Edit config.toml and add new provider section
cat >> ~/.codex/config.toml << 'EOF'

[model_providers.custom]
name = "My Custom Provider"
base_url = "https://my-api.example.com/v1"
env_key = "MY_API_KEY"
wire_api = "chat"
EOF
```

**Enable debug logging:**

```bash
export RUST_LOG=debug
# Then restart server
```

#### ⚠️ Important: Restart Required

**The HTTP server must be restarted after any configuration changes.** Configuration is loaded only at startup.

```bash
# 1. Stop the current server (Ctrl+C if running in foreground)
# 2. Restart with new configuration
./start_server.sh
```

#### Verification Steps

After making changes and restarting:

```bash
# 1. Check configuration display (server will show current config)
./start_server.sh

# 2. Verify with health check
python test_client.py --health-only

# 3. Test with actual request
python test_client.py --message "test message"
```

### Production Considerations

For production environments, you should:

1. Configure proper authentication and authorization
2. Set up CORS policies for web clients
3. Configure logging and monitoring
4. Use HTTPS/TLS encryption
5. Implement rate limiting
6. Validate and sanitize inputs

## Development

To modify the server:

1. Edit `src/main.rs` for the main server logic
2. Update `Cargo.toml` for dependencies
3. Test with `cargo check -p codex-http-server`
4. Run with `cargo run -p codex-http-server`

## Security Notes

This is a basic implementation intended for development and testing. For production use, consider adding:

- Authentication and authorization
- Rate limiting
- Input validation and sanitization
- HTTPS/TLS support
- CORS configuration
- Error handling improvements
