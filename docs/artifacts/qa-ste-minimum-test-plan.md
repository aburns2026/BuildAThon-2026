# QA/STE Test Plan (Current State)

Date: 2026-05-15
Stack: FastAPI API + React UI + Playwright TypeScript

## Current Automated Evidence

- API suite: 43 passed
- Playwright suite: 12 passed
- Frontend unit suite: 3 passed
- Backend coverage: 90%

## Frontend Unit Coverage

Files currently in scope:

- code/frontend/src/App.test.tsx

The frontend unit suite verifies:

- shell rendering with default empty-state responses
- backend error detail propagation for failed punch attempts
- enterprise admin and reporting summaries rendering from mocked API payloads

## API Test Coverage

Files currently in scope:

- code/tests/api/test_health.py
- code/tests/api/test_time_capture.py
- code/tests/api/test_expansion_contracts.py
- code/tests/api/test_phase2_contracts.py
- code/tests/api/test_repository_logic.py
- code/tests/api/test_security_hardening.py
- code/tests/api/test_compose_smoke.py (gated by `RUN_COMPOSE_SMOKE=1`)

The API suite verifies:

- time capture happy paths and rejection paths
- audit-event persistence and read models
- missing punch detection and attendance exceptions
- time corrections, leave workflows, leave balances, and scheduled shifts
- payroll summary, timesheets, breakdown, PTO, comp time, payroll export, and integration payloads
- operational reports, crosscheck reports, policy updates, and authorization checks
- direct repository logic for night-shift, holiday, payroll rollups, and compliance boundary cases
- authorization, role-claim, and company-claim enforcement
- gated docker-compose startup, backend health, and frontend reachability smoke coverage

## Playwright Coverage

Files currently in scope:

- code/tests/e2e/specs/main-path.spec.ts
- code/tests/e2e/specs/accessibility-pack.spec.ts
- code/tests/e2e/specs/mobile-accessibility.spec.ts
- code/tests/e2e/specs/leave-workflow.spec.ts
- code/tests/e2e/specs/scheduling-workflow.spec.ts
- code/tests/e2e/specs/negative-paths.spec.ts
- code/tests/e2e/specs/admin-reporting.spec.ts

The Playwright suite verifies:

- main browser punch flow from clock-in to clock-out
- leave request creation, manager approval, and leave-balance visibility
- manager scheduling workflow creation and scheduled-shift visibility
- duplicate punch rejection visibility
- shift history, payroll summary, payroll breakdown, compliance visibility, and audit visibility in the UI
- skip link, headings, landmarks, accessible names, live-region messaging, and keyboard interaction
- responsive/mobile accessibility baseline
- invalid scheduling, duplicate leave approval rejection, auth-failure messaging, and initial-load fallback behavior
- enterprise admin directory, location coverage, policy editing, employee reassignment, notification/secret stub configuration, operational summaries, crosscheck status, and payroll export readiness visibility

## Highest-Value Remaining QA Gaps

- The React UI now covers baseline enterprise admin and reporting management flows, but broader company operations and richer drill-down reporting are still untested in the browser.
- The React UI now has a small component/unit-test baseline, but coverage is still centered on the single App component.
- Runtime stack startup is now covered by a gated compose smoke test, but it is not part of the default fast suite.
- Downstream notification delivery and real secret-provider integrations are still stubbed, so automated tests only validate the configuration surfaces.

## Demo Evidence To Show

- API test output for the full API suite
- Playwright output for the full frontend suite
- archived screenshots under artifacts/playwright-runs/
- one clear explanation of which requirements are API-backed only versus UI-backed

## Suggested Commands

- API tests:
  - PYTHONPATH=$PWD/code pytest --cov=app code/tests/api
- Frontend unit tests:
  - cd code/frontend && npm test
- Playwright tests:
  - cd code/tests/e2e && npx playwright test
