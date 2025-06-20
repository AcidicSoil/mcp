#!/usr/bin/env bash
set -euo pipefail
echo "Tidying artefacts…"
pnpm store prune
pnpm exec rimraf dist coverage || true