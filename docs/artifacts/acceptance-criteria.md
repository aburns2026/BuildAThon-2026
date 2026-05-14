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

## EXP-A1 Missing Punch Detection Flag
- Given an open shift older than threshold, when detection runs, then the shift is marked as a missing-punch exception.
- Given an open shift newer than threshold, when detection runs, then it is not marked as missing-punch.
- Given a closed shift, when detection runs, then it is not included in missing-punch exceptions.

## EXP-A2 Missing Punch Exceptions List
- Given one or more missing-punch exceptions, when exceptions endpoint is requested, then response includes employee_id, shift_id, start_at, elapsed_minutes, and status.
- Given no exceptions, when endpoint is requested, then an empty list is returned safely.
- Given invalid employee context, when endpoint is requested, then response returns explicit validation error.

## EXP-A3 Exception Visibility In UI
- Given exceptions exist, when UI refreshes, then an exceptions section lists them.
- Given no exceptions, when UI refreshes, then section shows explicit empty state.
- Given API error, when UI refreshes, then user sees safe error text without stack details.

## EXP-B1 Leave Request Workflow
- Given valid leave dates, when employee submits request, then request is persisted as pending.

## EXP-B2 Leave Approval Workflow
- Given pending leave request, when manager approval is submitted, then request status becomes approved.

## EXP-B3 Leave Balance Visibility
- Given approved leave requests, when leave balance is requested, then used and remaining days are returned.

## EXP-B4 Shift Scheduling Baseline
- Given schedule payload, when scheduled shift is created, then schedule record is retrievable for the employee.

## EXP-C1 Payroll Breakdown Baseline
- Given employee payroll breakdown request, when endpoint is called, then breakdown payload includes base and placeholder compensation fields.

## EXP-D1 Compliance Report Skeleton
- Given compliance report request, when endpoint is called, then compliance payload returns validation statuses and exception count.

## EXP-E1 Enterprise Company/Location Baseline
- Given company identifier, when employees are listed, then response includes employees scoped to the company.

## Role-Coverage Acceptance Criteria
- Given PO/BA role gates, when planning artifacts are reviewed, then prioritization and traceability are explicit.
- Given QA/Security role gates, when evidence artifacts are reviewed, then pass/fail and risk decisions are explicit.
- Given Platform/Support role gates, when operations are reviewed, then startup/test paths and triage workflows are explicit.
