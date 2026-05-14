from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import desc

from backend.db import SessionLocal
from backend.main import app
from backend.models import Shift


client = TestClient(app)


def auth_headers(token: str = "demo-employee-token", extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if extra:
        headers.update(extra)
    return headers


def _create_closed_shift(duration_minutes: int = 600, start_hour_utc: int = 9) -> None:
    assert client.post("/employees/E001/clock-in", headers=auth_headers()).status_code == 200
    db = SessionLocal()
    try:
        shift = (
            db.query(Shift)
            .filter(Shift.employee_id == "E001", Shift.state == "OPEN")
            .order_by(desc(Shift.start_at))
            .first()
        )
        assert shift is not None
        start_dt = datetime.now(UTC).replace(hour=start_hour_utc, minute=0, second=0, microsecond=0)
        shift.start_at = start_dt - timedelta(minutes=duration_minutes)
        db.commit()
    finally:
        db.close()
    assert client.post("/employees/E001/clock-out", headers=auth_headers()).status_code == 200


def test_schedule_shift_hard_enforces_break_and_core_hour_policies() -> None:
    invalid_break = client.post(
        "/employees/E001/scheduled-shifts",
        json={
            "start_at": "2026-05-15T11:00:00+00:00",
            "end_at": "2026-05-15T14:00:00+00:00",
            "break_minutes": 10,
        },
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert invalid_break.status_code == 422
    assert "break_minutes" in invalid_break.json()["detail"]

    invalid_core_hours = client.post(
        "/employees/E001/scheduled-shifts",
        json={
            "start_at": "2026-05-15T11:00:00+00:00",
            "end_at": "2026-05-15T14:00:00+00:00",
            "break_minutes": 30,
        },
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert invalid_core_hours.status_code == 422
    assert invalid_core_hours.json()["detail"] == "scheduled shift must cover configured core hours"

    exceptions = client.get("/employees/E001/attendance-exceptions", headers=auth_headers())
    assert exceptions.status_code == 200
    assert exceptions.json()["exceptions"] == []


def test_timesheet_contract_and_period_validation() -> None:
    _create_closed_shift(duration_minutes=120)

    timesheet = client.get(
        "/employees/E001/timesheets",
        params={"period_start": "2026-01-01", "period_end": "2026-12-31"},
        headers=auth_headers(),
    )
    assert timesheet.status_code == 200
    body = timesheet.json()
    assert body["employee_id"] == "E001"
    assert body["total_minutes"] >= 0

    invalid = client.get(
        "/employees/E001/timesheets",
        params={"period_start": "2026-06-01", "period_end": "2026-05-01"},
        headers=auth_headers(),
    )
    assert invalid.status_code == 422


def test_pto_balance_and_adjustment() -> None:
    adjusted = client.post(
        "/employees/E001/pto-adjustments",
        json={"days_delta": 2},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert adjusted.status_code == 200

    balance = client.get("/employees/E001/pto-balance", headers=auth_headers())
    assert balance.status_code == 200
    assert balance.json()["total_days"] == 22


def test_comp_time_balance_and_adjustment() -> None:
    _create_closed_shift(duration_minutes=540)

    adjusted = client.post(
        "/employees/E001/comp-time-adjustments",
        json={"minutes_delta": 30, "reason": "Manual correction"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert adjusted.status_code == 200

    balance = client.get("/employees/E001/comp-time-balance", headers=auth_headers())
    assert balance.status_code == 200
    assert balance.json()["total_comp_time_minutes"] >= 90


def test_payroll_export_and_integration_payload() -> None:
    _create_closed_shift(duration_minutes=120)

    forbidden = client.get("/companies/COMP-001/payroll-export")
    assert forbidden.status_code == 401

    export_res = client.get(
        "/companies/COMP-001/payroll-export",
        params={"period_start": "2026-01-01", "period_end": "2026-12-31"},
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-001"}),
    )
    assert export_res.status_code == 200
    export_body = export_res.json()
    assert export_body["company_id"] == "COMP-001"
    assert export_body["status"] == "READY"

    integration = client.get(
        "/companies/COMP-001/payroll-integration-payload",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-001"}),
    )
    assert integration.status_code == 200
    assert integration.json()["schema_version"] == "1.0"


def test_location_scoped_endpoints() -> None:
    _create_closed_shift(duration_minutes=120)

    locations = client.get("/companies/COMP-001/locations", headers=auth_headers())
    assert locations.status_code == 200
    assert locations.json()["company_id"] == "COMP-001"
    assert locations.json()["locations"][0]["location_id"] == "LOC-001"

    location_employees = client.get(
        "/companies/COMP-001/locations/LOC-001/employees",
        headers=auth_headers(),
    )
    assert location_employees.status_code == 200
    assert len(location_employees.json()["employees"]) >= 1

    missing_location = client.get(
        "/companies/COMP-001/locations/LOC-999/employees",
        headers=auth_headers(),
    )
    assert missing_location.status_code == 404

    forbidden = client.get("/companies/COMP-001/locations/LOC-001/payroll-export")
    assert forbidden.status_code == 401

    allowed = client.get(
        "/companies/COMP-001/locations/LOC-001/payroll-export",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-001"}),
    )
    assert allowed.status_code == 200
    body = allowed.json()
    assert body["location_id"] == "LOC-001"
    assert body["status"] == "READY"


def test_operational_and_crosscheck_reports() -> None:
    _create_closed_shift(duration_minutes=120)

    report = client.get(
        "/reports/operational",
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert report.status_code == 200
    assert "event_count" in report.json()

    crosscheck = client.get(
        "/reports/crosscheck",
        params={"employee_id": "E001"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert crosscheck.status_code == 200
    assert crosscheck.json()["status"] in {"MATCH", "MISMATCH"}


def test_policy_config_and_authz_check() -> None:
    current = client.get("/policies", headers=auth_headers())
    assert current.status_code == 200

    forbidden = client.patch("/policies", json={"minimum_break_minutes": 45})
    assert forbidden.status_code == 401

    updated = client.patch(
        "/policies",
        json={"minimum_break_minutes": 45, "core_hour_start": 9, "core_hour_end": 16},
        headers=auth_headers("demo-admin-token", {"x-role": "ADMIN"}),
    )
    assert updated.status_code == 200
    assert updated.json()["policies"]["minimum_break_minutes"] == 45

    allow = client.post(
        "/authz/check",
        json={"role": "MANAGER", "action": "approve_leave"},
        headers=auth_headers(),
    )
    assert allow.status_code == 200
    assert allow.json()["allowed"] is True

    deny = client.post(
        "/authz/check",
        json={"role": "EMPLOYEE", "action": "policy_configure"},
        headers=auth_headers(),
    )
    assert deny.status_code == 200
    assert deny.json()["allowed"] is False
