#!/bin/bash

# Codex HTTP Server Startup Script

echo "🚀 Starting Codex HTTP Server..."
echo ""

# Check if cargo is available
if ! command -v cargo &> /dev/null; then
    echo "❌ Error: cargo is not installed or not in PATH"
    echo "Please install Rust and Cargo: https://rustup.rs/"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "Cargo.toml" ]; then
    echo "❌ Error: Not in the correct directory"
    echo "Please run this script from the codex-rs/http-server directory"
    exit 1
fi

# Function to find codex home directory (respects CODEX_HOME env var)
find_codex_home() {
    if [ -n "$CODEX_HOME" ]; then
        echo "$CODEX_HOME"
    else
        # $HOME already works correctly in Git Bash on Windows
        echo "$HOME/.codex"
    fi
}

# Function to read config from config.toml in codex home
read_config_value() {
    local key=$1
    local codex_home=$(find_codex_home)
    local config_file="$codex_home/config.toml"

    if [ -f "$config_file" ]; then
        grep "^$key = " "$config_file" | sed 's/.*= *"\(.*\)".*/\1/' | sed 's/.*= *\(.*\)/\1/' | tr -d '"'
    fi
}

# Read current configuration dynamically
CONFIG_MODEL=$(read_config_value "model")
CONFIG_PROVIDER=$(read_config_value "model_provider")
CONFIG_APPROVAL=$(read_config_value "approval_policy")

# Get base URL from provider config if available
CONFIG_BASE_URL=""
codex_home=$(find_codex_home)
config_file_path="$codex_home/config.toml"

if [ -f "$config_file_path" ] && grep -q "\[model_providers.ollama\]" "$config_file_path"; then
    CONFIG_BASE_URL=$(grep -A 5 "\[model_providers.ollama\]" "$config_file_path" | grep "base_url" | sed 's/.*= *"\(.*\)".*/\1/')
fi

# Export environment variables to ensure they take precedence over built-in defaults
# This is crucial because environment variables have higher precedence than config.toml
export CODEX_MODEL="${CODEX_MODEL:-$CONFIG_MODEL}"
export CODEX_PROVIDER="${CODEX_PROVIDER:-$CONFIG_PROVIDER}"
export CODEX_APPROVAL_POLICY="${CODEX_APPROVAL_POLICY:-$CONFIG_APPROVAL}"

# Critical: Export base URL from config (override existing if different)
if [ -n "$CONFIG_BASE_URL" ]; then
    if [ "$OLLAMA_BASE_URL" != "$CONFIG_BASE_URL" ]; then
        echo "🔧 Overriding OLLAMA_BASE_URL: '$OLLAMA_BASE_URL' → '$CONFIG_BASE_URL'"
        export OLLAMA_BASE_URL="$CONFIG_BASE_URL"
    else
        echo "🔧 OLLAMA_BASE_URL already correct: $OLLAMA_BASE_URL"
    fi
fi

# Display current configuration
echo "🔧 Configuration:"
echo "   Model: ${CODEX_MODEL:-${CONFIG_MODEL:-not set}}"
echo "   Provider: ${CODEX_PROVIDER:-${CONFIG_PROVIDER:-not set}}"
echo "   Base URL: ${OLLAMA_BASE_URL:-${CONFIG_BASE_URL:-not set}}"
echo "   Approval Policy: ${CODEX_APPROVAL_POLICY:-${CONFIG_APPROVAL:-not set}}"
echo "   Config File: $config_file_path $([ -f "$config_file_path" ] && echo "(exists)" || echo "(missing)")"
echo ""

# Check if LM Studio is running
if ! curl -s "http://localhost:1234/v1/models" > /dev/null 2>&1; then
    echo "⚠️  Warning: LM Studio doesn't appear to be running on localhost:1234"
    echo "   Please make sure LM Studio is running with the local server enabled"
    echo ""
fi

echo "🔧 Building the server..."
cargo build --release

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🌐 Starting server on http://127.0.0.1:8080"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""

    # Run the server (specify the binary explicitly)
    cargo run --release --bin codex-http-server
else
    echo "❌ Build failed!"
    exit 1
fi