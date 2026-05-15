from datetime import UTC, datetime, timedelta
from fastapi.testclient import TestClient

import backend.main as main
from backend.main import app


client = TestClient(app)


def auth_headers(token: str = "demo-employee-token", extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if extra:
        headers.update(extra)
    return headers


def test_clock_in_success() -> None:
    response = client.post("/employees/E001/clock-in", headers=auth_headers())

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == "E001"
    assert body["status"] == "CLOCKED_IN"
    assert "shift_id" in body
    assert "clock_in_at" in body


def test_duplicate_clock_in_rejected() -> None:
    first = client.post("/employees/E001/clock-in", headers=auth_headers())
    assert first.status_code == 200

    response = client.post("/employees/E001/clock-in", headers=auth_headers())

    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate clock-in: open shift exists"


def test_clock_out_success_after_open_shift() -> None:
    opened = client.post("/employees/E001/clock-in", headers=auth_headers())
    assert opened.status_code == 200

    response = client.post("/employees/E001/clock-out", headers=auth_headers())

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == "E001"
    assert body["status"] == "CLOCKED_OUT"
    assert isinstance(body["duration_minutes"], int)
    assert body["duration_minutes"] >= 0


def test_get_shifts_returns_closed_shift_history() -> None:
    assert client.post("/employees/E001/clock-in", headers=auth_headers()).status_code == 200
    assert client.post("/employees/E001/clock-out", headers=auth_headers()).status_code == 200

    response = client.get("/employees/E001/shifts", headers=auth_headers())

    assert response.status_code == 200
    body = response.json()
    assert "shifts" in body
    assert len(body["shifts"]) == 1
    shift = body["shifts"][0]
    assert shift["employee_id"] == "E001"
    assert shift["state"] == "CLOSED"
    assert isinstance(shift["duration_minutes"], int)


def test_get_audit_events_returns_punch_event_history() -> None:
    assert client.post("/employees/E001/clock-in", headers=auth_headers()).status_code == 200
    assert client.post("/employees/E001/clock-out", headers=auth_headers()).status_code == 200

    response = client.get("/employees/E001/audit-events", headers=auth_headers())

    assert response.status_code == 200
    body = response.json()
    assert "events" in body
    assert len(body["events"]) >= 2
    event_types = [event["event_type"] for event in body["events"]]
    assert "CLOCK_IN_ACCEPTED" in event_types
    assert "CLOCK_OUT_ACCEPTED" in event_types


def test_get_payroll_summary_returns_closed_shift_totals() -> None:
    assert client.post("/employees/E001/clock-in", headers=auth_headers()).status_code == 200
    assert client.post("/employees/E001/clock-out", headers=auth_headers()).status_code == 200

    response = client.get(
        "/employees/E001/payroll-summary",
        params={"period_start": "2026-05-14", "period_end": "2026-05-14"},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == "E001"
    assert body["closed_shift_count"] == 1
    assert isinstance(body["total_minutes_worked"], int)
    assert body["total_minutes_worked"] >= 0
    assert body["period_start"] == "2026-05-14"
    assert body["period_end"] == "2026-05-14"


def test_missing_punch_exceptions_empty_for_recent_open_shift() -> None:
    assert client.post("/employees/E001/clock-in", headers=auth_headers()).status_code == 200

    response = client.get(
        "/employees/E001/missing-punch-exceptions",
        params={"threshold_minutes": 60},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["threshold_minutes"] == 60
    assert body["exceptions"] == []


def test_missing_punch_exceptions_flag_for_old_open_shift(monkeypatch) -> None:
    started_at = datetime(2026, 5, 15, 9, 0, tzinfo=UTC)
    monkeypatch.setattr(main, "utc_now", lambda: started_at)
    assert client.post("/employees/E001/clock-in", headers=auth_headers()).status_code == 200

    monkeypatch.setattr(main, "utc_now", lambda: started_at + timedelta(minutes=120))

    response = client.get(
        "/employees/E001/missing-punch-exceptions",
        params={"threshold_minutes": 60},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["exceptions"]) == 1
    exception = body["exceptions"][0]
    assert exception["employee_id"] == "E001"
    assert exception["status"] == "MISSING_PUNCH"
    assert exception["elapsed_minutes"] >= 120


def test_missing_punch_exceptions_invalid_threshold_rejected() -> None:
    response = client.get(
        "/employees/E001/missing-punch-exceptions",
        params={"threshold_minutes": 0},
        headers=auth_headers(),
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "threshold_minutes must be greater than 0"
