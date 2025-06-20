# 🕹️ Codex Agent Contract (Node 22+)

## Contract: Task Completion

A task is **complete** only when _all_ commands below exit 0.

| Stage       | Command                 | Pass Criteria                 |
| ----------- | ----------------------- | ----------------------------- |
| Bootstrap   | `bash ./setup/entry.sh` | Script exits 0                |
| Unit tests  | `pnpm test`             | Vitest passes (all green ✔︎) |
| Type safety | `pnpm typecheck`        | No TypeScript errors          |
| Style       | `pnpm run lint`         | ESLint & Prettier clean       |

---

## Rust/codex-rs

In the `codex-rs` directory:

- **Do not** add or modify any code related to `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR`.
- The sandbox sets `CODEX_SANDBOX_NETWORK_DISABLED=1` for any shell tool use.
  If you see this env var in code/tests, it exists to skip tests that require outbound network access.

---

## Quickstart: One-liner for Humans

```bash
bash ./setup/entry.sh
```
