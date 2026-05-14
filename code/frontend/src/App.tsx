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

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://127.0.0.1:8000";

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
      },
      ...init,
    });
  }

  async function refreshReadModels() {
    const [shiftRes, auditRes, summaryRes] = await Promise.all([
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/shifts`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/audit-events`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/payroll-summary`),
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
    <main className="page">
      <section className="hero">
        <p className="eyebrow">BuildAThon 2026 MVP</p>
        <h1>Workforce Time Capture Console</h1>
        <p className="sub">Employee {DEMO_EMPLOYEE_ID} · {headerSub}</p>
      </section>

      <section className="controls card">
        <div className="button-row">
          <button disabled={busy} onClick={() => void runPunch("in")}>
            Clock In
          </button>
          <button className="secondary" disabled={busy} onClick={() => void runPunch("out")}>
            Clock Out
          </button>
        </div>
        <p className="message">{message}</p>
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
    </main>
  );
}
