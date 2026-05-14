# Validation Rules (Current State)

Date: 2026-05-14

## Identity and Access Rules

- Employee identifiers must match the expected `E###...` format.
- All non-health endpoints require a valid bearer token.
- `x-role` must match the authenticated principal when supplied.
- Company-scoped endpoints require a matching `x-company-id` claim.
- Admin-only policy changes require a role with `policy_configure` permission.

## Time Capture Rules

- Clock-in is rejected if an open shift already exists for the employee.
- Clock-out is rejected if no open shift exists for the employee.
- Only one open shift is allowed per employee at a time.
- Clock-out closes the current open shift and computes a non-negative duration.
- Audit records are written for accepted and rejected core punch actions.

## Date and Time Rules

- Leave request dates must be ISO dates.
- Scheduled shift timestamps must be ISO datetimes.
- End dates must be on or after start dates.
- Scheduled shift end time must be after start time.
- Optional period filters must respect period_start <= period_end.

## Scheduling and Policy Rules

- Missing punch threshold must be greater than 0.
- Scheduled shifts must satisfy configured minimum break minutes.
- Scheduled shifts must cover the configured core-hour window.
- Policy values must stay within bounded numeric ranges.
- `core_hour_start` must be earlier than `core_hour_end`.

## Input Quality Rules

- Time correction reason length is limited to 200 characters.
- Validation failures return explicit, safe, structured error payloads.
- Success payloads return enough state for clients to refresh read models without guessing business outcomes.

## Known Non-Validation Gaps

- Local development still defaults to SQLite even though the containerized deployment path now uses PostgreSQL.
- Runtime request counters remain instance-local rather than aggregated across replicas.
