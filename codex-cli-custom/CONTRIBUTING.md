# Contributing

This repository uses a split test strategy so everyday PRs remain fast.

## Running Tests

1. Bootstrap the project:

```bash
bash ./setup/entry.sh
```

2. Run the JS/TS checks:

```bash
pnpm test
pnpm typecheck
pnpm run lint
```

3. Run Python tests excluding heavy integration suites:

```bash
pytest -m "not docker and not integration"
```

Docker-based or network integration tests are marked with `docker` or `integration` and run separately in CI.
