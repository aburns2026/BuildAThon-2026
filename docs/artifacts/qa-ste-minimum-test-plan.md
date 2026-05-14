# QA/STE Test Plan (Current State)

Date: 2026-05-14
Stack: FastAPI API + React UI + Playwright TypeScript

## Current Automated Evidence

- API suite: 37 passed
- Playwright suite: 7 passed
- Backend coverage: 90%

## API Test Coverage

Files currently in scope:

- code/tests/api/test_health.py
- code/tests/api/test_time_capture.py
- code/tests/api/test_expansion_contracts.py
- code/tests/api/test_phase2_contracts.py
- code/tests/api/test_security_hardening.py

The API suite verifies:

- time capture happy paths and rejection paths
- audit-event persistence and read models
- missing punch detection and attendance exceptions
- time corrections, leave workflows, leave balances, and scheduled shifts
- payroll summary, timesheets, breakdown, PTO, comp time, payroll export, and integration payloads
- operational reports, crosscheck reports, policy updates, and authorization checks
- authorization, role-claim, and company-claim enforcement

## Playwright Coverage

Files currently in scope:

- code/tests/e2e/specs/main-path.spec.ts
- code/tests/e2e/specs/accessibility-pack.spec.ts
- code/tests/e2e/specs/mobile-accessibility.spec.ts
- code/tests/e2e/specs/leave-workflow.spec.ts
- code/tests/e2e/specs/scheduling-workflow.spec.ts

The Playwright suite verifies:

- main browser punch flow from clock-in to clock-out
- leave request creation, manager approval, and leave-balance visibility
- manager scheduling workflow creation and scheduled-shift visibility
- duplicate punch rejection visibility
- shift history, payroll summary, payroll breakdown, compliance visibility, and audit visibility in the UI
- skip link, headings, landmarks, accessible names, live-region messaging, and keyboard interaction
- responsive/mobile accessibility baseline

## Highest-Value Remaining QA Gaps

- The React UI does not yet cover enterprise admin workflows or broader reporting views.
- Runtime APIs and monitoring configs are validated, but stack startup and image-build checks are not yet part of the automated test suite.

## Demo Evidence To Show

- API test output for the full API suite
- Playwright output for the full frontend suite
- archived screenshots under artifacts/playwright-runs/
- one clear explanation of which requirements are API-backed only versus UI-backed

## Suggested Commands

- API tests:
  - PYTHONPATH=$PWD/code pytest --cov=app code/tests/api
- Playwright tests:
  - cd code/tests/e2e && npx playwright test
