# Planning Framework (Current Repository State)

Date: 2026-05-14
Primary source documents:
- docs/bbsi_buildathon_2026_requirements_only.md
- docs/Bbsi Buildathon 2026 Ade Guide.pdf

## Repository Posture

The repository started with a 4-hour MVP slice and has since expanded beyond that initial scope.
It now contains:

- a FastAPI backend that covers the full Section 4 functional surface through API contracts
- a React frontend that now covers time capture, leave and scheduling workflow basics, payroll detail, and compliance visibility
- API tests that cover core, expansion, phase-2, and security-hardening contracts
- Playwright coverage for the main path, accessibility, mobile accessibility baseline, leave workflow, and scheduling workflow

## Current Delivery Shape

### Backend and API Coverage
- Workforce time management: implemented
- Scheduling and leave management: implemented
- Payroll and compensation: implemented
- Compliance and reporting: implemented with baseline rule-based compliance validations
- Mobile workforce support: implemented at the responsive/accessibility baseline
- Enterprise readiness: implemented at the contract level, with scalability still limited by selected in-process state

### Frontend Coverage
- Implemented UI: clock-in, clock-out, shift history, payroll summary, payroll breakdown, compliance report, leave request/approval/balance, scheduling workflow, audit events, missing punch exceptions
- Responsive/mobile baseline: implemented
- Accessibility baseline: implemented
- Not yet implemented in UI: enterprise admin views and broader operational/company reporting views

## Verified Evidence Snapshot

- API tests: 37 passed
- Playwright tests: 7 passed
- Backend coverage: 90%

## Current Planning Priorities

1. Preserve alignment between source-of-truth requirements and living docs.
2. Keep delivery claims honest by distinguishing API-backed capabilities from UI-backed workflows.
3. Close the highest-value technical gaps before widening scope again.

## Highest-Value Remaining Gaps

### Product and Contract Gaps
- Enterprise scalability is only partial because local development still defaults to file-backed SQLite and runtime telemetry counters remain instance-local even though workflow and policy state are durable.

### Technical Requirement Gaps
- A monitoring stack is present, but downstream notification integrations and long-horizon operations workflows are still minimal.
- Secret handling is environment-configurable, but there is no dedicated secret-management integration.
- No event-driven integration contract exists yet.

## Recommended Next Phase

1. Expand the frontend for enterprise-admin and broader reporting workflows.
2. Add downstream alert receivers and secret-management integration.
3. Add event-driven integration posture if enterprise operations become a priority.
