#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -n "${PYTHON_BIN:-}" ]]; then
	python_bin="$PYTHON_BIN"
elif [[ -x "/workspaces/codespaces-blank/.venv/bin/python" ]]; then
	python_bin="/workspaces/codespaces-blank/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
	python_bin="$(command -v python3)"
else
	python_bin="$(command -v python)"
fi

echo "[test_runner] using python: $python_bin"

if [[ ! -d "$ROOT_DIR/code/frontend/node_modules" ]]; then
	echo "[test_runner] installing frontend dependencies"
	(cd "$ROOT_DIR/code/frontend" && npm install)
fi

if [[ ! -d "$ROOT_DIR/code/tests/e2e/node_modules" ]]; then
	echo "[test_runner] installing e2e dependencies"
	(cd "$ROOT_DIR/code/tests/e2e" && npm install)
fi

echo "[test_runner] running full API suite"
(cd "$ROOT_DIR" && PYTHONPATH="$ROOT_DIR/code" "$python_bin" -m pytest code/tests/api -q -k "not docker_compose_stack_starts_and_serves_health")

echo "[test_runner] running frontend component tests"
(cd "$ROOT_DIR/code/frontend" && npm test)

echo "[test_runner] running full Playwright suite"
(cd "$ROOT_DIR/code/tests/e2e" && npm test)

echo "[test_runner] validating compose config"
(cd "$ROOT_DIR" && docker compose config -q)

echo "[test_runner] running compose smoke"
(cd "$ROOT_DIR" && PYTHONPATH="$ROOT_DIR/code" "$python_bin" -m pytest code/tests/api/test_compose_smoke.py -q)

echo "[test_runner] all checks passed"