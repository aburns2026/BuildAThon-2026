# Support Triage Output (Step 6)

Date: 2026-05-14
Scope: MVP + post-MVP expansion operational triage (demo-friendly)

## 1. Likely Incident Types

- Duplicate punch accepted unexpectedly
- Clock-out rejected even though user believes they are clocked in
- Payroll summary shows lower total than expected
- UI status message appears stale after punch action
- Audit event not visible after successful clock-out
- Leave request cannot be created or approved
- Scheduled shift rejected due to invalid date-time window
- Compliance report or payroll breakdown appears inconsistent with shift data
- Ops diagnostics counters do not align with expected recent actions

## 2. Minimum Logging and Observability Needs

- API request log: method, route, employee_id, status_code, response_time_ms
- Business event log: CLOCK_IN_ACCEPTED, CLOCK_IN_REJECTED, CLOCK_OUT_ACCEPTED, CLOCK_OUT_REJECTED
- Error log: validation failures and exception summary without sensitive internals
- UI console capture during demo for failed network calls
- Request correlation by employee_id for all employee-scoped endpoints
- Lightweight periodic snapshot of `/ops/diagnostics` during demo runs

## 3. Triage Steps for Most Likely Incident (Invalid or Missing Punch)

1. Reproduce with employee E001 in UI.
2. Check UI message area for validation text.
3. Call API endpoint directly for same action and compare status code.
4. Fetch `/employees/E001/shifts` to confirm OPEN/CLOSED state.
5. Fetch `/employees/E001/audit-events` to confirm accepted/rejected event trail.
6. Confirm whether issue is data-state, validation-path, or UI-state display.

## 3b. Triage Steps for Expansion Incidents

### Leave Workflow Incident
1. Reproduce with `POST /employees/E001/leave-requests` using known-good ISO dates.
2. Verify request appears in `GET /employees/E001/leave-requests`.
3. Approve via `POST /leave-requests/{leaveRequestId}/approve`.
4. Confirm downstream impact in `GET /employees/E001/leave-balance`.
5. Validate audit lineage in `GET /employees/E001/audit-events`.

### Scheduling Incident
1. Submit known-good schedule to `POST /employees/E001/scheduled-shifts`.
2. If rejected, compare payload against ISO datetime requirement and start/end ordering.
3. Confirm persistence via `GET /employees/E001/scheduled-shifts`.
4. Check related event trace in `GET /employees/E001/audit-events`.

### Payroll/Compliance Incident
1. Verify source of truth with `GET /employees/E001/shifts` and open/closed states.
2. Recalculate expected totals from closed shifts.
3. Compare against `GET /employees/E001/payroll-summary` and `/payroll-breakdown`.
4. Validate exceptions used by compliance with `GET /employees/E001/missing-punch-exceptions`.
5. Check aggregate counters in `GET /ops/diagnostics` for drift clues.

## 4. Probable Root-Cause Categories

- State mismatch: open shift not where UI expects it
- Validation mismatch: duplicate/open-shift checks triggered as designed but misunderstood by caller
- UI rendering mismatch: status text or history not refreshed after action
- Timing/data setup mismatch: test/demo actions executed out of expected order
- Input-format mismatch: invalid employee ID, date, or datetime rejected by validation guardrails
- Cross-endpoint expectation mismatch: user expectation differs from contract semantics
- Data reset/fixture mismatch between test and manual demo flows

## 5. Smallest Sensible Operations Next Step

Add one concise troubleshooting note for demo operators:
- If punch behavior looks wrong, run shifts endpoint and audit-events endpoint for E001 first.
- This gives immediate truth on shift state and event lineage before code changes.

Add one compact support runbook card in demo notes:
- Incident -> Primary endpoint checks -> Expected response shape -> Escalation owner.

## 6. Quick Triage Commands (Demo Operator)

- Punch state:
	- `curl -s http://127.0.0.1:8000/employees/E001/shifts | jq`
	- `curl -s http://127.0.0.1:8000/employees/E001/audit-events | jq`
- Missing punch:
	- `curl -s "http://127.0.0.1:8000/employees/E001/missing-punch-exceptions?threshold_minutes=60" | jq`
- Leave flow:
	- `curl -s http://127.0.0.1:8000/employees/E001/leave-requests | jq`
	- `curl -s http://127.0.0.1:8000/employees/E001/leave-balance | jq`
- Scheduling:
	- `curl -s http://127.0.0.1:8000/employees/E001/scheduled-shifts | jq`
- Ops health snapshot:
	- `curl -s http://127.0.0.1:8000/ops/diagnostics | jq`
