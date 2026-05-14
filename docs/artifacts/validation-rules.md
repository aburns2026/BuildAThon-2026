# MVP Validation Rules (PO/BA)

## Core Rules
- Employee identifier is required for all time-capture endpoints.
- Clock-in is rejected if an open shift already exists for the employee.
- Clock-out is rejected if no open shift exists for the employee.
- Timestamps must be server-generated or validated against a safe format if client-provided.
- Validation errors return clear, safe, non-sensitive messages.

## Data Integrity Rules
- Only one open shift is allowed per employee at a time.
- Clock-out closes the most recent open shift for the employee.
- Duration is non-negative.
- Audit records are written for successful and rejected punch attempts when feasible.

## Response Rules
- Validation failures return structured error payloads.
- Success payloads include enough fields for UI state updates without extra calls where practical.

## Expansion Rules (Phase A)
- Missing-punch threshold must be a positive integer in minutes.
- Only OPEN shifts are eligible for missing-punch detection.
- Elapsed time for missing-punch detection is computed in UTC.
- Missing-punch exceptions endpoint must return deterministic empty lists when no exceptions exist.
- UI must tolerate exceptions-endpoint failures and show a safe fallback message.
