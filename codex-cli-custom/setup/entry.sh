# setup/entry.sh
#!/usr/bin/env bash
set -euo pipefail
NODE_VERSION="${NODE_VERSION:-22}"        # override: export NODE_VERSION=24
PNPM_VERSION="${PNPM_VERSION:-9.1.1}"
here() { cd -- "$(dirname "$0")"; }      # run from setup/
log()  { printf "\n\033[36m>> %s\033[0m\n" "$*"; }

here
log "Bootstrapping Node $NODE_VERSION + pnpm $PNPM_VERSION…"
./node.sh "$NODE_VERSION" "$PNPM_VERSION"

log "Running quality gates (lint • typecheck • test)…"
pnpm run lint
pnpm run typecheck
pnpm test

log "Setup finished ✓"