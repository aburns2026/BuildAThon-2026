# BuildAThon-2026

Current-state workspace for the BBSI BuildAThon Workforce Time Tracking and Payroll Integration Platform.

The source-of-truth documents are:

- docs/bbsi_buildathon_2026_requirements_only.md
- docs/Bbsi Buildathon 2026 Ade Guide.pdf

The markdown files under docs/artifacts/ are working documents that now reflect the repository's current implementation state rather than only the original MVP plan.

## Current Implementation Snapshot

- Backend: FastAPI API covering all Section 4 functional requirements through contract endpoints, plus selected Section 5 technical baselines.
- Frontend: React browser workflow covering time capture, leave request and approval, scheduling, leave balance visibility, payroll breakdown visibility, compliance reporting visibility, audit events, missing punch visibility, and responsive/accessibility baseline behavior.
- Platform assets: request logging with request-id correlation, `/metrics` and enriched health/diagnostics endpoints, backend/frontend Dockerfiles, a PostgreSQL-backed docker-compose path, and an external Prometheus/Alertmanager/Grafana monitoring stack.
- Automated evidence: 37 passing API tests, 7 passing Playwright tests, and 90% backend coverage.

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
