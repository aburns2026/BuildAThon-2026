from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_clock_in_success() -> None:
    response = client.post("/employees/E001/clock-in")

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == "E001"
    assert body["status"] == "CLOCKED_IN"
    assert "shift_id" in body
    assert "clock_in_at" in body


def test_duplicate_clock_in_rejected() -> None:
    first = client.post("/employees/E001/clock-in")
    assert first.status_code in (200, 409)

    response = client.post("/employees/E001/clock-in")

    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate clock-in: open shift exists"


def test_clock_out_success_after_open_shift() -> None:
    maybe_open = client.post("/employees/E001/clock-in")
    assert maybe_open.status_code in (200, 409)

    response = client.post("/employees/E001/clock-out")

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == "E001"
    assert body["status"] == "CLOCKED_OUT"
    assert isinstance(body["duration_minutes"], int)
    assert body["duration_minutes"] >= 0


def test_get_shifts_returns_closed_shift_history() -> None:
    assert client.post("/employees/E001/clock-in").status_code == 200
    assert client.post("/employees/E001/clock-out").status_code == 200

    response = client.get("/employees/E001/shifts")

    assert response.status_code == 200
    body = response.json()
    assert "shifts" in body
    assert len(body["shifts"]) == 1
    shift = body["shifts"][0]
    assert shift["employee_id"] == "E001"
    assert shift["state"] == "CLOSED"
    assert isinstance(shift["duration_minutes"], int)


def test_get_audit_events_returns_punch_event_history() -> None:
    assert client.post("/employees/E001/clock-in").status_code == 200
    assert client.post("/employees/E001/clock-out").status_code == 200

    response = client.get("/employees/E001/audit-events")

    assert response.status_code == 200
    body = response.json()
    assert "events" in body
    assert len(body["events"]) >= 2
    event_types = [event["event_type"] for event in body["events"]]
    assert "CLOCK_IN_ACCEPTED" in event_types
    assert "CLOCK_OUT_ACCEPTED" in event_types


def test_get_payroll_summary_returns_closed_shift_totals() -> None:
    assert client.post("/employees/E001/clock-in").status_code == 200
    assert client.post("/employees/E001/clock-out").status_code == 200

    response = client.get(
        "/employees/E001/payroll-summary",
        params={"period_start": "2026-05-14", "period_end": "2026-05-14"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == "E001"
    assert body["closed_shift_count"] == 1
    assert isinstance(body["total_minutes_worked"], int)
    assert body["total_minutes_worked"] >= 0
    assert body["period_start"] == "2026-05-14"
    assert body["period_end"] == "2026-05-14"
