#!/usr/bin/env bash
set -euo pipefail
NODE_VERSION="${1:-22}"
PNPM_VERSION="${2:-latest}"

# Install Node with Volta (works without sudo in Codex sandbox)
curl -fsSL https://get.volta.sh | bash -s -- --skip-setup
export VOLTA_HOME="$HOME/.volta"; export PATH="$VOLTA_HOME/bin:$PATH"
volta install "node@$NODE_VERSION"

corepack enable && corepack prepare "pnpm@$PNPM_VERSION" --activate

pnpm install --frozen-lockfile --prefer-offline --reporter=silent
pnpm exec husky install || true   # init hooks once per clone