# BuildAThon-2026

Current-state workspace for the BBSI BuildAThon Workforce Time Tracking and Payroll Integration Platform.

The source-of-truth documents are:

- docs/bbsi_buildathon_2026_requirements_only.md
- docs/Bbsi Buildathon 2026 Ade Guide.pdf

The markdown files under docs/artifacts/ are working documents that now reflect the repository's current implementation state rather than only the original MVP plan.

## Current Implementation Snapshot

- Backend: FastAPI API covering all Section 4 functional requirements through contract endpoints, plus selected Section 5 technical baselines.
- Frontend: React browser workflow covering time capture, leave request and approval, scheduling, leave balance visibility, payroll breakdown visibility, compliance reporting visibility, enterprise admin directory/location views, editable policy and location management, stubbed notification and secret-provider configuration, operational reporting summaries, audit events, missing punch visibility, and responsive/accessibility baseline behavior.
- Platform assets: request logging with request-id correlation, `/metrics` and enriched health/diagnostics endpoints, backend/frontend Dockerfiles, a PostgreSQL-backed docker-compose path, and an external Prometheus/Alertmanager/Grafana monitoring stack.
- Automated evidence: API, frontend, Playwright, and compose smoke validation are bundled in the required `test_runner` script.

## Demo Boundary

The browser demo is intentionally narrower than the full API surface.

UI-backed demo flows:

- punch management
- leave request and approval
- scheduling
- payroll summary and breakdown visibility
- compliance and missing-punch visibility
- enterprise admin directory, location, policy, notification-stub, and secret-provider stub flows
- operational reporting summary and payroll export readiness

API-only surfaces that should not be oversold as browser-demo features:

- PTO balance and PTO adjustments
- comp-time balance and comp-time adjustments
- payroll integration payload generation
- authz check
- ops diagnostics
- location-scoped payroll export variants beyond the summary/readiness view

## Structure

- docs/
  - source requirements and working project artifacts
- artifacts/playwright-runs/
  - archived Playwright screenshots by run id
- code/backend/
  - FastAPI service, database models, repositories, and migrations
- code/frontend/
  - React UI for the implemented browser workflow slice
- code/tests/api/
  - contract, regression, and security-hardening API tests
- code/tests/e2e/
  - Playwright main-path, leave, scheduling, accessibility, and mobile accessibility tests

## Start Here

1. Review docs/artifacts/planning-framework.md for the current implementation posture.
2. Review docs/artifacts/requirements-traceability-matrix.md for requirement-to-delivery status.
3. Use the README files under code/frontend and code/tests/e2e for local run and test commands.
4. Use docker-compose.yml if you want a containerized demo and monitoring path.

## Test Runner

Run the required `test_runner` before treating the build as demo-ready:

```bash
./scripts/test_runner.sh
```

That runner executes the full API suite, frontend component tests, full Playwright suite, docker compose validation, and the compose smoke test.

## Clean Demo Start

The default local SQLite path persists data between runs. If you want a clean demo boot instead of reopening prior local state, start the backend with reset-on-startup enabled:

```bash
cd code/backend
RESET_DATABASE_ON_STARTUP=1 ENABLE_DEMO_RESET_ENDPOINTS=1 DEMO_RESET_TOKEN=demo-reset uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

That boot path resets the local database, reseeds the demo employee and policy defaults, and gives the frontend a clean initial UI state.

If you need to clear a running non-test demo instance without restarting it, use the gated demo reset endpoint:

```bash
curl -X POST http://127.0.0.1:8000/demo-support/reset -H 'x-demo-reset-token: demo-reset'
```

Leave `ENABLE_DEMO_RESET_ENDPOINTS` unset in normal non-demo runs.
