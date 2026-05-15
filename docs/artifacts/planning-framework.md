# Planning Framework (Current Repository State)

Date: 2026-05-15
Primary source documents:
- docs/bbsi_buildathon_2026_requirements_only.md
- docs/Bbsi Buildathon 2026 Ade Guide.pdf

## Repository Posture

The repository started with a 4-hour MVP slice and has since expanded beyond that initial scope.
It now contains:

- a FastAPI backend that covers the full Section 4 functional surface through API contracts
- a React frontend that now covers time capture, leave and scheduling workflow basics, payroll detail, compliance visibility, baseline enterprise admin/reporting views, and simple editable admin workflows
- API tests that cover core, expansion, phase-2, and security-hardening contracts
- frontend unit tests for the main App shell and selected error/rendering paths
- Playwright coverage for the main path, accessibility, mobile accessibility baseline, leave workflow, scheduling workflow, admin/reporting visibility, and targeted negative paths

## Current Delivery Shape

### Backend and API Coverage
- Workforce time management: implemented
- Scheduling and leave management: implemented
- Payroll and compensation: implemented
- Compliance and reporting: implemented with baseline rule-based compliance validations
- Mobile workforce support: implemented at the responsive/accessibility baseline
- Enterprise readiness: implemented at the contract level, with scalability still limited by selected in-process state

### Frontend Coverage
- Implemented UI: clock-in, clock-out, shift history, payroll summary, payroll breakdown, compliance report, leave request/approval/balance, scheduling workflow, enterprise admin company directory, location coverage, policy editing, employee location reassignment, stub notification configuration/testing, stub secret-provider configuration, operational summary, crosscheck summary, payroll export readiness, audit events, missing punch exceptions
- Responsive/mobile baseline: implemented
- Accessibility baseline: implemented
- Remaining API-only UI gaps: deeper enterprise admin actions, richer drill-down reporting, and broader company/location management workflows

## Verified Evidence Snapshot

- API tests: 43 passed
- Playwright tests: 12 passed
- Frontend unit tests: 3 passed
- Backend coverage: 90%
- Review check: markdown artifacts re-verified against code and tests on 2026-05-15

## Current Planning Priorities

1. Preserve alignment between source-of-truth requirements and living docs.
2. Keep delivery claims honest by distinguishing API-backed capabilities from UI-backed workflows.
3. Close the highest-value technical gaps before widening scope again.

## Highest-Value Remaining Gaps

### Product and Contract Gaps
- Enterprise scalability is only partial because local development still defaults to file-backed SQLite and runtime telemetry counters remain instance-local even though workflow and policy state are durable.

### Technical Requirement Gaps
- A monitoring stack is present, and the admin UI now exposes a downstream notification stub, but there is still no real receiver integration.
- Secret handling now has a reference-only admin stub, but there is still no dedicated secret-management integration.
- No event-driven integration contract exists yet.

### Test Posture Gaps
- Frontend now has a small React unit-test baseline, but component-level coverage is still thin relative to the size of App.tsx.
- Current Playwright coverage now includes targeted negative-path UI checks and editable admin/reporting baseline flows, but broader enterprise admin/reporting flows still need deeper UI workflows.

## Recommended Next Phase

1. Replace the notification and secret-management stubs with real provider integrations when infrastructure exists.
2. Deepen the admin surface beyond single-record management flows into broader company/location operations.
3. Add event-driven integration posture if enterprise operations become a priority.
