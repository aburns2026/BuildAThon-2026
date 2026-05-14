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

type MissingPunchException = {
  employee_id: string;
  shift_id: string;
  start_at: string;
  elapsed_minutes: number;
  status: "MISSING_PUNCH";
};

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://127.0.0.1:8000";
const API_BEARER_TOKEN =
  (import.meta.env.VITE_DEMO_AUTH_TOKEN as string | undefined) ?? "demo-employee-token";

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

export default function App() {
  const [message, setMessage] = useState("Ready");
  const [status, setStatus] = useState<"CLOCKED_IN" | "CLOCKED_OUT" | "UNKNOWN">("UNKNOWN");
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [summary, setSummary] = useState<PayrollSummary | null>(null);
  const [exceptions, setExceptions] = useState<MissingPunchException[]>([]);
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

  async function apiRequest(path: string, init?: RequestInit): Promise<Response> {
    return fetch(`${API_BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${API_BEARER_TOKEN}`,
      },
      ...init,
    });
  }

  async function refreshReadModels() {
    const [shiftRes, auditRes, summaryRes, exceptionRes] = await Promise.all([
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/shifts`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/audit-events`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/payroll-summary`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/missing-punch-exceptions?threshold_minutes=60`),
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

    if (exceptionRes.ok) {
      const exceptionBody = await exceptionRes.json();
      setExceptions(exceptionBody.exceptions ?? []);
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
        <p className="eyebrow">BuildAThon 2026 MVP</p>
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
