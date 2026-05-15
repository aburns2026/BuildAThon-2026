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


def _create_closed_shift(monkeypatch, employee_id: str, start_at: datetime, duration_minutes: int) -> None:
    ended_at = start_at + timedelta(minutes=duration_minutes)

    monkeypatch.setattr(main, "utc_now", lambda: start_at)
    assert client.post(f"/employees/{employee_id}/clock-in", headers=auth_headers()).status_code == 200

    monkeypatch.setattr(main, "utc_now", lambda: ended_at)
    assert client.post(f"/employees/{employee_id}/clock-out", headers=auth_headers()).status_code == 200


def test_create_and_list_time_corrections() -> None:
    created = client.post(
        "/employees/E001/time-corrections",
        json={"reason": "Forgot to clock out"},
        headers=auth_headers(),
    )
    assert created.status_code == 200

    listed = client.get("/employees/E001/time-corrections", headers=auth_headers())
    assert listed.status_code == 200
    assert listed.json()["time_corrections"] == [
        {
            "correction_id": created.json()["correction_id"],
            "employee_id": "E001",
            "reason": "Forgot to clock out",
            "requested_at": created.json()["requested_at"],
            "status": "PENDING",
        }
    ]


def test_create_approve_leave_and_balance() -> None:
    created = client.post(
        "/employees/E001/leave-requests",
        json={"start_date": "2026-05-20", "end_date": "2026-05-21"},
        headers=auth_headers(),
    )
    assert created.status_code == 200
    leave_id = created.json()["leave_request_id"]

    approved = client.post(
        f"/leave-requests/{leave_id}/approve",
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"

    duplicate_approval = client.post(
        f"/leave-requests/{leave_id}/approve",
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert duplicate_approval.status_code == 409
    assert duplicate_approval.json()["detail"] == "Leave request already approved"

    balance = client.get("/employees/E001/leave-balance", headers=auth_headers())
    assert balance.status_code == 200
    assert balance.json()["used_days"] == 2
    assert balance.json()["remaining_days"] == 18

    pto_balance = client.get("/employees/E001/pto-balance", headers=auth_headers())
    assert pto_balance.status_code == 200
    assert pto_balance.json()["used_days"] == 2
    assert pto_balance.json()["remaining_days"] == 18


def test_schedule_shift_and_list() -> None:
    created = client.post(
        "/employees/E001/scheduled-shifts",
        json={"start_at": "2026-05-15T09:00:00+00:00", "end_at": "2026-05-15T17:00:00+00:00"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert created.status_code == 200

    listed = client.get("/employees/E001/scheduled-shifts", headers=auth_headers())
    assert listed.status_code == 200
    assert listed.json()["scheduled_shifts"] == [
        {
            "scheduled_shift_id": created.json()["scheduled_shift_id"],
            "employee_id": "E001",
            "start_at": "2026-05-15T09:00:00",
            "end_at": "2026-05-15T17:00:00",
            "break_minutes": 30,
            "break_compliant": True,
            "covers_core_hours": True,
            "status": "SCHEDULED",
        }
    ]


def test_payroll_breakdown_and_compliance_report(monkeypatch) -> None:
    _create_closed_shift(monkeypatch, "E001", datetime(2026, 5, 15, 9, 0, tzinfo=UTC), 600)
    _create_closed_shift(monkeypatch, "E001", datetime(2026, 5, 16, 23, 0, tzinfo=UTC), 120)

    breakdown = client.get("/employees/E001/payroll-breakdown", headers=auth_headers())
    assert breakdown.status_code == 200
    assert breakdown.json() == {
        "employee_id": "E001",
        "total_minutes_worked": 720,
        "regular_minutes": 600,
        "overtime_minutes": 120,
        "holiday_minutes": 120,
        "night_shift_minutes": 120,
    }

    compliance = client.get("/employees/E001/compliance-report", headers=auth_headers())
    assert compliance.status_code == 200
    compliance_body = compliance.json()
    assert compliance_body["tax_validation_status"] == "PASS"
    assert compliance_body["labor_rule_validation_status"] == "PASS"
    tax_rules = {item["rule"]: item for item in compliance_body["tax_validations"]}
    labor_rules = {item["rule"]: item for item in compliance_body["labor_rule_validations"]}
    assert tax_rules["EMPLOYEE_ORG_ASSIGNMENT_PRESENT"]["status"] == "PASS"
    assert tax_rules["TAXABLE_TIME_PRESENT"]["status"] == "PASS"
    assert labor_rules["ATTENDANCE_EXCEPTIONS_CLEAR"]["status"] == "PASS"
    assert labor_rules["NO_OPEN_SHIFT_PENDING"]["status"] == "PASS"
    assert labor_rules["MAX_SHIFT_DURATION_UNDER_12_HOURS"]["status"] == "PASS"


def test_company_listing_and_ops_diagnostics(monkeypatch) -> None:
    _create_closed_shift(monkeypatch, "E001", datetime(2026, 5, 15, 9, 0, tzinfo=UTC), 120)

    correction = client.post(
        "/employees/E001/time-corrections",
        json={"reason": "Forgot to clock out"},
        headers=auth_headers(),
    )
    assert correction.status_code == 200

    leave = client.post(
        "/employees/E001/leave-requests",
        json={"start_date": "2026-05-20", "end_date": "2026-05-21"},
        headers=auth_headers(),
    )
    assert leave.status_code == 200

    scheduled = client.post(
        "/employees/E002/scheduled-shifts",
        json={"start_at": "2026-05-15T09:00:00+00:00", "end_at": "2026-05-15T17:00:00+00:00"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert scheduled.status_code == 200

    pto_adjustment = client.post(
        "/employees/E001/pto-adjustments",
        json={"days_delta": 2},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert pto_adjustment.status_code == 200

    comp_adjustment = client.post(
        "/employees/E001/comp-time-adjustments",
        json={"minutes_delta": 15, "reason": "Payroll correction"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert comp_adjustment.status_code == 200

    company = client.get("/companies/COMP-001/employees", headers=auth_headers())
    assert company.status_code == 200
    assert company.json()["employees"] == [
        {"employee_id": "E001", "company_id": "COMP-001", "location_id": "LOC-001"},
        {"employee_id": "E002", "company_id": "COMP-001", "location_id": "LOC-002"},
    ]

    diagnostics = client.get("/ops/diagnostics", headers=auth_headers())
    assert diagnostics.status_code == 200
    body = diagnostics.json()
    assert body["open_shift_count"] == 0
    assert body["shift_count"] == 1
    assert body["audit_event_count"] == 7
    assert body["leave_request_count"] == 1
    assert body["scheduled_shift_count"] == 1
    assert body["time_correction_count"] == 1
    assert body["pto_adjustment_count"] == 1
    assert body["comp_time_adjustment_count"] == 1
    assert body["policy_count"] == 3
    assert body["request_count_total"] == 8
    assert body["request_error_count"] == 0
    assert body["request_duration_ms_max"] >= 0
    assert body["database_status"] == "ok"
    assert body["database_backend"] == "sqlite"
