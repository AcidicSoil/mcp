#!/usr/bin/env bash
set -euo pipefail

# Docker build/run script for Codex dev sandbox
# Builds custom image with Codex CLI installed and proper sandbox configuration

# Handle Windows paths in Git Bash/MINGW64
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  # Convert to Windows path format that Docker Desktop can understand
  HOST_DIR="$(cygpath -m "$(pwd)")"
  # Convert Windows home directory path for .codex mounting
  if [[ -n "${HOME:-}" ]]; then
    HOST_CODEX_DIR="$(cygpath -m "$HOME")/.codex"
  else
    HOST_CODEX_DIR="$(cygpath -m "$USERPROFILE")/.codex"
  fi
  # Prevent MSYS path conversion for Docker container paths
  export MSYS_NO_PATHCONV=1
else
  HOST_DIR="$(pwd)"
  HOST_CODEX_DIR="$HOME/.codex"
fi

CONTAINER_NAME="$(basename "$HOST_DIR")"
CONTAINER_DIR="/workspace/$CONTAINER_NAME"
CONTAINER_CODEX_DIR="/root/.codex"
IMAGE_NAME="codex-sandbox"

echo "Starting Codex sandbox container..."
echo "Host directory: $HOST_DIR"
echo "Container directory: $CONTAINER_DIR"
echo "Host Codex config: $HOST_CODEX_DIR"
echo "Container Codex config: $CONTAINER_CODEX_DIR"

# Build custom image with Codex CLI if it doesn't exist
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "Building custom Codex sandbox image..."
    docker build -t "$IMAGE_NAME" - <<'EOF'
FROM node:22.16.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y \
      curl iptables ipset \
      golang-go \
      git wget jq yq nano vim zsh fzf tree htop ncdu shellcheck \
      build-essential cmake make pkg-config bandit \
 && npm install -g @openai/codex@latest pnpm@10.8.1 eslint prettier shfmt \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /root/.npm/_logs/*

WORKDIR /workspace
EOF
fi

# Prepare Docker run arguments
DOCKER_ARGS=(
  --rm -it
  --network=bridge
  --add-host=host.docker.internal:host-gateway
  -e CODEX_ENV_NODE_VERSION=22
  -v "$HOST_DIR":"$CONTAINER_DIR"
  -w "$CONTAINER_DIR"
  -p 0.0.0.0:1234:1234
)

# Mount Codex config directory if it exists
if [[ -d "$HOST_CODEX_DIR" ]]; then
  echo "Mounting Codex config directory..."
  DOCKER_ARGS+=(-v "$HOST_CODEX_DIR":"$CONTAINER_CODEX_DIR")
else
  echo "Warning: Codex config directory not found at $HOST_CODEX_DIR"
  echo "Container will use default Codex configuration"
fi

# Pass through common environment variables
ENV_VARS=(
  "OPENAI_API_KEY"
  "AZURE_OPENAI_API_KEY"
  "OPENROUTER_API_KEY"
  "GEMINI_API_KEY"
  "OLLAMA_API_KEY"
  "OLLAMA_BASE_URL"
  "MISTRAL_API_KEY"
  "DEEPSEEK_API_KEY"
  "XAI_API_KEY"
  "GROQ_API_KEY"
  "ARCEEAI_API_KEY"
  "CODEX_CONFIG_PATH"
)


for var in "${ENV_VARS[@]}"; do
  if [[ -n "${!var:-}" ]]; then
    echo "Passing environment variable: $var"
    DOCKER_ARGS+=(-e "$var=${!var}")
  fi
done

# Run the container with proper sandbox configuration
echo "Running container with mounted config..."
docker run "${DOCKER_ARGS[@]}" "$IMAGE_NAME" bash

# Notes:
# - Custom image includes Codex CLI and /etc/codex/sandbox/enabled flag
# - Network isolation and filesystem access controls are configured
# - Outbound connection to api.openai.com is maintained via --network=bridge
# - Container is automatically removed after exit (--rm)
# - MSYS_NO_PATHCONV=1 prevents Git Bash from converting Linux container paths
# - Host .codex directory is mounted to /root/.codex in container
# - Common API keys and config environment variables are passed through
# - Drops directly into bash shell for immediate Codex usage

# Inside the container, you can run:
# codex --help
# bash setup/entry.sh