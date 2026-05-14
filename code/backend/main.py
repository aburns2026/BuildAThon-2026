from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


DEMO_EMPLOYEES = {"E001"}
OPEN_SHIFTS: dict[str, dict] = {}
SHIFTS: list[dict] = []
AUDIT_EVENTS: list[dict] = []


def employee_exists(employee_id: str) -> bool:
    return employee_id in DEMO_EMPLOYEES


def add_audit_event(employee_id: str, event_type: str, details: str) -> None:
    AUDIT_EVENTS.append(
        {
            "event_id": str(uuid4()),
            "employee_id": employee_id,
            "event_type": event_type,
            "event_at": utc_now_iso(),
            "details": details,
        }
    )

app = FastAPI(title="BuildAThon 2026 MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "timestamp": utc_now_iso()}


@app.post("/employees/{employee_id}/clock-in")
def clock_in(employee_id: str) -> dict:
    if not employee_exists(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    if employee_id in OPEN_SHIFTS:
        add_audit_event(employee_id, "CLOCK_IN_REJECTED", "Duplicate open shift")
        raise HTTPException(status_code=409, detail="Duplicate clock-in: open shift exists")

    shift = {
        "shift_id": str(uuid4()),
        "employee_id": employee_id,
        "start_at": utc_now_iso(),
        "end_at": None,
        "duration_minutes": None,
        "state": "OPEN",
    }
    OPEN_SHIFTS[employee_id] = shift
    SHIFTS.append(shift)
    add_audit_event(employee_id, "CLOCK_IN_ACCEPTED", "Clock-in accepted")

    return {
        "shift_id": shift["shift_id"],
        "employee_id": employee_id,
        "status": "CLOCKED_IN",
        "clock_in_at": shift["start_at"],
    }


@app.post("/employees/{employee_id}/clock-out")
def clock_out(employee_id: str) -> dict:
    if not employee_exists(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    shift = OPEN_SHIFTS.get(employee_id)
    if shift is None:
        add_audit_event(employee_id, "CLOCK_OUT_REJECTED", "No open shift")
        raise HTTPException(status_code=409, detail="Clock-out rejected: no open shift exists")

    end_dt = datetime.now(UTC)
    start_dt = datetime.fromisoformat(shift["start_at"])
    duration_minutes = max(0, int((end_dt - start_dt).total_seconds() // 60))

    shift["end_at"] = end_dt.isoformat()
    shift["duration_minutes"] = duration_minutes
    shift["state"] = "CLOSED"
    OPEN_SHIFTS.pop(employee_id, None)
    add_audit_event(employee_id, "CLOCK_OUT_ACCEPTED", "Clock-out accepted")

    return {
        "shift_id": shift["shift_id"],
        "employee_id": employee_id,
        "status": "CLOCKED_OUT",
        "clock_out_at": shift["end_at"],
        "duration_minutes": duration_minutes,
    }


@app.get("/employees/{employee_id}/shifts")
def get_shifts(employee_id: str, limit: int = 10) -> dict:
    if not employee_exists(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    safe_limit = max(1, min(limit, 100))
    employee_shifts = [s for s in SHIFTS if s["employee_id"] == employee_id]
    return {"shifts": employee_shifts[-safe_limit:]}


@app.get("/employees/{employee_id}/audit-events")
def get_audit_events(employee_id: str, limit: int = 20) -> dict:
    if not employee_exists(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    safe_limit = max(1, min(limit, 100))
    employee_events = [e for e in AUDIT_EVENTS if e["employee_id"] == employee_id]
    return {"events": employee_events[-safe_limit:]}


@app.get("/employees/{employee_id}/payroll-summary")
def get_payroll_summary(
    employee_id: str,
    period_start: str | None = None,
    period_end: str | None = None,
) -> dict:
    if not employee_exists(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    closed_shifts = [
        shift
        for shift in SHIFTS
        if shift["employee_id"] == employee_id and shift["state"] == "CLOSED"
    ]
    total_minutes_worked = sum(shift["duration_minutes"] or 0 for shift in closed_shifts)

    return {
        "employee_id": employee_id,
        "total_minutes_worked": total_minutes_worked,
        "closed_shift_count": len(closed_shifts),
        "period_start": period_start,
        "period_end": period_end,
    }
