import { useEffect, useMemo, useState } from "react";

type Shift = {
  shift_id: string;
  employee_id: string;
  start_at: string;
  end_at: string | null;
  duration_minutes: number | null;
  state: "OPEN" | "CLOSED";
};

type AuditEvent = {
  event_id: string;
  employee_id: string;
  event_type: string;
  event_at: string;
  details: string;
};

type PayrollSummary = {
  employee_id: string;
  total_minutes_worked: number;
  closed_shift_count: number;
  period_start: string | null;
  period_end: string | null;
};

type PayrollBreakdown = {
  employee_id: string;
  total_minutes_worked: number;
  regular_minutes: number;
  overtime_minutes: number;
  holiday_minutes: number;
  night_shift_minutes: number;
};

type MissingPunchException = {
  employee_id: string;
  shift_id: string;
  start_at: string;
  elapsed_minutes: number;
  status: "MISSING_PUNCH";
};

type LeaveRequest = {
  leave_request_id: string;
  employee_id: string;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
  approved_at: string | null;
};

type LeaveBalance = {
  employee_id: string;
  total_days: number;
  used_days: number;
  remaining_days: number;
};

type ScheduledShift = {
  scheduled_shift_id: string;
  employee_id: string;
  start_at: string;
  end_at: string;
  break_minutes: number;
  break_compliant: boolean;
  covers_core_hours: boolean;
  status: string;
};

type PolicyConfig = {
  minimum_break_minutes: number;
  core_hour_start: number;
  core_hour_end: number;
};

type ComplianceValidation = {
  rule: string;
  status: "PASS" | "WARN" | "FAIL";
  details: string;
};

type ComplianceReport = {
  employee_id: string;
  tax_validation_status: "PASS" | "WARN" | "FAIL";
  labor_rule_validation_status: "PASS" | "WARN" | "FAIL";
  attendance_exception_count: number;
  tax_validations: ComplianceValidation[];
  labor_rule_validations: ComplianceValidation[];
};

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://127.0.0.1:8000";
const API_BEARER_TOKEN =
  (import.meta.env.VITE_DEMO_AUTH_TOKEN as string | undefined) ?? "demo-employee-token";
const API_MANAGER_TOKEN =
  (import.meta.env.VITE_MANAGER_AUTH_TOKEN as string | undefined) ?? "demo-manager-token";

const DEMO_EMPLOYEE_ID = "E001";

function formatDate(value: string | null): string {
  if (!value) {
    return "-";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString();
}

function formatMinutes(value: number): string {
  return `${value} min`;
}

function formatRuleLabel(value: string): string {
  return value.replace(/_/g, " ");
}

function getStatusClassName(value: string): string {
  return `status-pill ${value.toLowerCase()}`;
}

export default function App() {
  const [message, setMessage] = useState("Ready");
  const [status, setStatus] = useState<"CLOCKED_IN" | "CLOCKED_OUT" | "UNKNOWN">("UNKNOWN");
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [summary, setSummary] = useState<PayrollSummary | null>(null);
  const [payrollBreakdown, setPayrollBreakdown] = useState<PayrollBreakdown | null>(null);
  const [complianceReport, setComplianceReport] = useState<ComplianceReport | null>(null);
  const [exceptions, setExceptions] = useState<MissingPunchException[]>([]);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [leaveBalance, setLeaveBalance] = useState<LeaveBalance | null>(null);
  const [scheduledShifts, setScheduledShifts] = useState<ScheduledShift[]>([]);
  const [policyConfig, setPolicyConfig] = useState<PolicyConfig | null>(null);
  const [leaveStartDate, setLeaveStartDate] = useState("2026-05-20");
  const [leaveEndDate, setLeaveEndDate] = useState("2026-05-21");
  const [scheduledStartAt, setScheduledStartAt] = useState("2026-05-22T09:00");
  const [scheduledEndAt, setScheduledEndAt] = useState("2026-05-22T17:00");
  const [scheduledBreakMinutes, setScheduledBreakMinutes] = useState("30");
  const [busy, setBusy] = useState(false);

  const headerSub = useMemo(
    () =>
      status === "UNKNOWN"
        ? "No recent action"
        : status === "CLOCKED_IN"
          ? "Employee currently clocked in"
          : "Employee currently clocked out",
    [status]
  );

  async function apiRequest(
    path: string,
    init?: RequestInit,
    options?: { token?: string; extraHeaders?: Record<string, string> }
  ): Promise<Response> {
    return fetch(`${API_BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${options?.token ?? API_BEARER_TOKEN}`,
        ...(options?.extraHeaders ?? {}),
      },
      ...init,
    });
  }

  async function refreshReadModels() {
    const [
      shiftRes,
      auditRes,
      summaryRes,
      breakdownRes,
      complianceRes,
      exceptionRes,
      leaveRequestRes,
      leaveBalanceRes,
      scheduledShiftRes,
      policiesRes,
    ] = await Promise.all([
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/shifts`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/audit-events`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/payroll-summary`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/payroll-breakdown`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/compliance-report`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/missing-punch-exceptions?threshold_minutes=60`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/leave-requests`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/leave-balance`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/scheduled-shifts`),
      apiRequest(`/policies`),
    ]);

    if (shiftRes.ok) {
      const shiftBody = await shiftRes.json();
      setShifts(shiftBody.shifts ?? []);
    }

    if (auditRes.ok) {
      const auditBody = await auditRes.json();
      setEvents(auditBody.events ?? []);
    }

    if (summaryRes.ok) {
      const summaryBody = await summaryRes.json();
      setSummary(summaryBody);
    }

    if (breakdownRes.ok) {
      const breakdownBody = await breakdownRes.json();
      setPayrollBreakdown(breakdownBody);
    }

    if (complianceRes.ok) {
      const complianceBody = await complianceRes.json();
      setComplianceReport(complianceBody);
    }

    if (exceptionRes.ok) {
      const exceptionBody = await exceptionRes.json();
      setExceptions(exceptionBody.exceptions ?? []);
    }

    if (leaveRequestRes.ok) {
      const leaveRequestBody = await leaveRequestRes.json();
      setLeaveRequests(leaveRequestBody.leave_requests ?? []);
    }

    if (leaveBalanceRes.ok) {
      const leaveBalanceBody = await leaveBalanceRes.json();
      setLeaveBalance(leaveBalanceBody);
    }

    if (scheduledShiftRes.ok) {
      const scheduledShiftBody = await scheduledShiftRes.json();
      setScheduledShifts(scheduledShiftBody.scheduled_shifts ?? []);
    }

    if (policiesRes.ok) {
      const policiesBody = await policiesRes.json();
      setPolicyConfig(policiesBody.policies ?? null);
    }
  }

  async function runPunch(action: "in" | "out") {
    setBusy(true);
    const endpoint =
      action === "in"
        ? `/employees/${DEMO_EMPLOYEE_ID}/clock-in`
        : `/employees/${DEMO_EMPLOYEE_ID}/clock-out`;

    try {
      const response = await apiRequest(endpoint, { method: "POST" });
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Request failed");
      } else {
        const newStatus = body.status as "CLOCKED_IN" | "CLOCKED_OUT";
        setStatus(newStatus);
        setMessage(
          action === "in"
            ? `Clock-in accepted at ${formatDate(body.clock_in_at)}`
            : `Clock-out accepted at ${formatDate(body.clock_out_at)}`
        );
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function submitLeaveRequest(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/leave-requests`, {
        method: "POST",
        body: JSON.stringify({ start_date: leaveStartDate, end_date: leaveEndDate }),
      });
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Leave request failed");
      } else {
        setMessage(`Leave request created for ${body.start_date} to ${body.end_date}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function approveLeaveRequest(leaveRequestId: string) {
    setBusy(true);

    try {
      const response = await apiRequest(
        `/leave-requests/${leaveRequestId}/approve`,
        { method: "POST" },
        { token: API_MANAGER_TOKEN, extraHeaders: { "x-role": "MANAGER" } }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Leave approval failed");
      } else {
        setMessage(`Leave request approved for ${body.start_date} to ${body.end_date}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function submitScheduledShift(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(
        `/employees/${DEMO_EMPLOYEE_ID}/scheduled-shifts`,
        {
          method: "POST",
          body: JSON.stringify({
            start_at: new Date(scheduledStartAt).toISOString(),
            end_at: new Date(scheduledEndAt).toISOString(),
            break_minutes: Number(scheduledBreakMinutes),
          }),
        },
        { token: API_MANAGER_TOKEN, extraHeaders: { "x-role": "MANAGER" } }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Scheduling request failed");
      } else {
        setMessage(`Scheduled shift created for ${formatDate(body.start_at)} to ${formatDate(body.end_at)}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void refreshReadModels();
  }, []);

  useEffect(() => {
    if (shifts.length === 0) {
      return;
    }
    const latest = shifts[shifts.length - 1];
    setStatus(latest.state === "OPEN" ? "CLOCKED_IN" : "CLOCKED_OUT");
  }, [shifts]);

  return (
    <main id="main-content" className="page" aria-labelledby="app-title">
      <a href="#main-content" className="skip-link">Skip to content</a>

      <section className="hero" aria-label="Application heading">
        <p className="eyebrow">BuildAThon 2026 Current-State Demo</p>
        <h1 id="app-title">Workforce Time Capture Console</h1>
        <p className="sub">Employee {DEMO_EMPLOYEE_ID} · {headerSub}</p>
      </section>

      <section className="controls card" aria-label="Punch controls">
        <div className="button-row">
          <button
            type="button"
            disabled={busy}
            aria-label={`Clock in employee ${DEMO_EMPLOYEE_ID}`}
            onClick={() => void runPunch("in")}
          >
            Clock In
          </button>
          <button
            type="button"
            className="secondary"
            disabled={busy}
            aria-label={`Clock out employee ${DEMO_EMPLOYEE_ID}`}
            onClick={() => void runPunch("out")}
          >
            Clock Out
          </button>
        </div>
        <p className="message" role="status" aria-live="polite">
          {message}
        </p>
      </section>

      <section className="grid">
        <article className="card">
          <h2>Shift History</h2>
          {shifts.length === 0 ? (
            <p className="empty">No shifts yet.</p>
          ) : (
            <ul className="list">
              {shifts
                .slice()
                .reverse()
                .map((shift) => (
                  <li key={shift.shift_id}>
                    <div>
                      <strong>{shift.state}</strong>
                      <span>
                        {formatDate(shift.start_at)} {" -> "} {formatDate(shift.end_at)}
                      </span>
                    </div>
                    <span>{shift.duration_minutes ?? 0} min</span>
                  </li>
                ))}
            </ul>
          )}
        </article>

        <article className="card">
          <h2>Payroll Summary</h2>
          {!summary ? (
            <p className="empty">No summary available.</p>
          ) : (
            <dl className="summary">
              <div>
                <dt>Total Minutes</dt>
                <dd>{summary.total_minutes_worked}</dd>
              </div>
              <div>
                <dt>Closed Shifts</dt>
                <dd>{summary.closed_shift_count}</dd>
              </div>
            </dl>
          )}
        </article>

        <article className="card">
          <h2>Payroll Breakdown</h2>
          {!payrollBreakdown ? (
            <p className="empty">No payroll breakdown available.</p>
          ) : (
            <dl className="summary">
              <div>
                <dt>Total Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.total_minutes_worked)}</dd>
              </div>
              <div>
                <dt>Regular Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.regular_minutes)}</dd>
              </div>
              <div>
                <dt>Overtime Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.overtime_minutes)}</dd>
              </div>
              <div>
                <dt>Holiday Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.holiday_minutes)}</dd>
              </div>
              <div>
                <dt>Night Shift Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.night_shift_minutes)}</dd>
              </div>
            </dl>
          )}
        </article>

        <article className="card compliance-card">
          <h2>Compliance Report</h2>
          {!complianceReport ? (
            <p className="empty">No compliance report available.</p>
          ) : (
            <div className="card-stack">
              <dl className="summary compliance-summary">
                <div>
                  <dt>Tax Validation Status</dt>
                  <dd>
                    <span className={getStatusClassName(complianceReport.tax_validation_status)}>
                      {complianceReport.tax_validation_status}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt>Labor Validation Status</dt>
                  <dd>
                    <span className={getStatusClassName(complianceReport.labor_rule_validation_status)}>
                      {complianceReport.labor_rule_validation_status}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt>Attendance Exceptions</dt>
                  <dd>{complianceReport.attendance_exception_count}</dd>
                </div>
              </dl>

              <div className="validation-columns">
                <section aria-label="Tax validations">
                  <p className="section-label">Tax Validations</p>
                  <ul className="list validation-list">
                    {complianceReport.tax_validations.map((validation) => (
                      <li key={validation.rule}>
                        <div>
                          <strong>{formatRuleLabel(validation.rule)}</strong>
                          <span>{validation.details}</span>
                        </div>
                        <span className={getStatusClassName(validation.status)}>{validation.status}</span>
                      </li>
                    ))}
                  </ul>
                </section>

                <section aria-label="Labor validations">
                  <p className="section-label">Labor Validations</p>
                  <ul className="list validation-list">
                    {complianceReport.labor_rule_validations.map((validation) => (
                      <li key={validation.rule}>
                        <div>
                          <strong>{formatRuleLabel(validation.rule)}</strong>
                          <span>{validation.details}</span>
                        </div>
                        <span className={getStatusClassName(validation.status)}>{validation.status}</span>
                      </li>
                    ))}
                  </ul>
                </section>
              </div>
            </div>
          )}
        </article>
      </section>

      <section className="card leave-card">
        <h2>Leave Workflow</h2>
        <form className="leave-form" onSubmit={(event) => void submitLeaveRequest(event)}>
          <label>
            <span>Leave start date</span>
            <input
              type="date"
              value={leaveStartDate}
              onChange={(event) => setLeaveStartDate(event.target.value)}
            />
          </label>
          <label>
            <span>Leave end date</span>
            <input
              type="date"
              value={leaveEndDate}
              onChange={(event) => setLeaveEndDate(event.target.value)}
            />
          </label>
          <button type="submit" disabled={busy}>
            Submit Leave Request
          </button>
        </form>

        {leaveBalance ? (
          <dl className="summary leave-summary">
            <div>
              <dt>Total Days</dt>
              <dd>{leaveBalance.total_days}</dd>
            </div>
            <div>
              <dt>Used Days</dt>
              <dd>{leaveBalance.used_days}</dd>
            </div>
            <div>
              <dt>Remaining Days</dt>
              <dd>{leaveBalance.remaining_days}</dd>
            </div>
          </dl>
        ) : (
          <p className="empty">No leave balance available.</p>
        )}

        {leaveRequests.length === 0 ? (
          <p className="empty">No leave requests yet.</p>
        ) : (
          <ul className="list leave-list">
            {leaveRequests
              .slice()
              .reverse()
              .map((request) => (
                <li key={request.leave_request_id}>
                  <div>
                    <strong>{request.status}</strong>
                    <span>
                      {request.start_date} to {request.end_date}
                    </span>
                  </div>
                  {request.status === "PENDING" ? (
                    <button
                      type="button"
                      className="secondary"
                      disabled={busy}
                      onClick={() => void approveLeaveRequest(request.leave_request_id)}
                    >
                      Approve Leave Request
                    </button>
                  ) : (
                    <span>{request.approved_at ? `Approved ${formatDate(request.approved_at)}` : "Approved"}</span>
                  )}
                </li>
              ))}
          </ul>
        )}
      </section>

      <section className="card scheduling-card">
        <h2>Scheduling Workflow</h2>
        <form className="schedule-form" onSubmit={(event) => void submitScheduledShift(event)}>
          <label>
            <span>Scheduled start</span>
            <input
              type="datetime-local"
              value={scheduledStartAt}
              onChange={(event) => setScheduledStartAt(event.target.value)}
            />
          </label>
          <label>
            <span>Scheduled end</span>
            <input
              type="datetime-local"
              value={scheduledEndAt}
              onChange={(event) => setScheduledEndAt(event.target.value)}
            />
          </label>
          <label>
            <span>Break minutes</span>
            <input
              type="number"
              min={policyConfig?.minimum_break_minutes ?? 1}
              step="1"
              value={scheduledBreakMinutes}
              onChange={(event) => setScheduledBreakMinutes(event.target.value)}
            />
          </label>
          <button type="submit" disabled={busy}>
            Schedule Shift
          </button>
        </form>

        {policyConfig ? (
          <dl className="summary schedule-policy-summary">
            <div>
              <dt>Minimum Break</dt>
              <dd>{policyConfig.minimum_break_minutes} min</dd>
            </div>
            <div>
              <dt>Core Hours</dt>
              <dd>
                {policyConfig.core_hour_start}:00 - {policyConfig.core_hour_end}:00
              </dd>
            </div>
          </dl>
        ) : (
          <p className="empty">Policy guidance unavailable.</p>
        )}

        {scheduledShifts.length === 0 ? (
          <p className="empty">No scheduled shifts yet.</p>
        ) : (
          <ul className="list schedule-list">
            {scheduledShifts
              .slice()
              .reverse()
              .map((shift) => (
                <li key={shift.scheduled_shift_id}>
                  <div>
                    <strong>{shift.status}</strong>
                    <span>
                      {formatDate(shift.start_at)} {" -> "} {formatDate(shift.end_at)}
                    </span>
                    <span>
                      Break {shift.break_minutes} min · Core hours {shift.covers_core_hours ? "covered" : "missed"}
                    </span>
                  </div>
                  <span>{shift.break_compliant ? "Break compliant" : "Break issue"}</span>
                </li>
              ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h2>Audit Events</h2>
        {events.length === 0 ? (
          <p className="empty">No audit events yet.</p>
        ) : (
          <ul className="list">
            {events
              .slice()
              .reverse()
              .map((event) => (
                <li key={event.event_id}>
                  <div>
                    <strong>{event.event_type}</strong>
                    <span>{formatDate(event.event_at)}</span>
                  </div>
                  <span>{event.details}</span>
                </li>
              ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h2>Missing Punch Exceptions</h2>
        {exceptions.length === 0 ? (
          <p className="empty">No missing punch exceptions.</p>
        ) : (
          <ul className="list">
            {exceptions.map((exception) => (
              <li key={exception.shift_id}>
                <div>
                  <strong>{exception.status}</strong>
                  <span>Shift {exception.shift_id}</span>
                </div>
                <span>{exception.elapsed_minutes} min open</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
