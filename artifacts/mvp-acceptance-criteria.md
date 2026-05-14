# MVP Acceptance Criteria (PO/BA)

## MVP-1 Clock-In
- Given a valid employee with no open shift, when clock-in is submitted, then a punch-in is stored and an open shift is created.
- Given successful clock-in, when the response returns, then status shows clocked-in with a recorded timestamp.
- Given a valid clock-in request, when processing completes, then an audit event is recorded for the action.

## MVP-2 Duplicate Clock-In Prevention
- Given an employee with an existing open shift, when another clock-in is submitted, then the request is rejected.
- Given duplicate clock-in rejection, when response returns, then a clear validation message explains why it failed.
- Given duplicate rejection, when processing completes, then an audit event is recorded for the rejected action.

## MVP-3 Clock-Out
- Given an employee with an open shift, when clock-out is submitted, then the shift is closed and duration is computed.
- Given successful clock-out, when response returns, then status shows clocked-out with a recorded timestamp.
- Given successful clock-out, when processing completes, then an audit event is recorded.

## MVP-4 Shift History or Today Summary
- Given an employee with recorded shifts, when history or summary is requested, then results include at least start, end, and duration fields.
- Given no recorded shifts, when history is requested, then an empty result is returned safely.
- Given API retrieval, when data is displayed in UI, then validation and error states are visible.

## MVP-5 Audit Visibility
- Given punch success or rejection, when audit events are requested, then entries include event type, actor or source, timestamp, and target employee context.
- Given audit retrieval, when no events exist, then an empty list is returned safely.

## MVP-6 Payroll-Ready Summary
- Given completed shifts, when payroll summary is requested, then total worked duration for the selected period is returned.
- Given an open shift not yet closed, when payroll summary is requested, then behavior is deterministic and documented (excluded or flagged).
- Given summary response, when consumed by downstream flow, then payload is simple and stable.
