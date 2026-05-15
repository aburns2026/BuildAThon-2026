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


def _create_closed_shift_at(monkeypatch, start_at: datetime, duration_minutes: int, employee_id: str = "E001") -> None:
    ended_at = start_at + timedelta(minutes=duration_minutes)

    monkeypatch.setattr(main, "utc_now", lambda: start_at)
    assert client.post(f"/employees/{employee_id}/clock-in", headers=auth_headers()).status_code == 200

    monkeypatch.setattr(main, "utc_now", lambda: ended_at)
    assert client.post(f"/employees/{employee_id}/clock-out", headers=auth_headers()).status_code == 200


def _create_closed_shift(monkeypatch, duration_minutes: int = 600, start_hour_utc: int = 9) -> None:
    _create_closed_shift_at(
        monkeypatch,
        datetime(2026, 5, 15, start_hour_utc, 0, tzinfo=UTC),
        duration_minutes,
    )


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


def test_timesheet_contract_and_period_validation(monkeypatch) -> None:
    _create_closed_shift(monkeypatch, duration_minutes=120)

    timesheet = client.get(
        "/employees/E001/timesheets",
        params={"period_start": "2026-01-01", "period_end": "2026-12-31"},
        headers=auth_headers(),
    )
    assert timesheet.status_code == 200
    body = timesheet.json()
    assert body["employee_id"] == "E001"
    assert body["total_minutes"] == 120
    assert len(body["entries"]) == 1
    assert body["entries"][0]["minutes"] == 120
    assert body["entries"][0]["date"] == "2026-05-15"

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


def test_comp_time_balance_and_adjustment(monkeypatch) -> None:
    _create_closed_shift(monkeypatch, duration_minutes=540)

    adjusted = client.post(
        "/employees/E001/comp-time-adjustments",
        json={"minutes_delta": 30, "reason": "Manual correction"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert adjusted.status_code == 200

    balance = client.get("/employees/E001/comp-time-balance", headers=auth_headers())
    assert balance.status_code == 200
    body = balance.json()
    assert body["accrued_from_overtime_minutes"] == 60
    assert body["manual_adjustment_minutes"] == 30
    assert body["total_comp_time_minutes"] == 90


def test_balance_adjustments_validate_non_zero_values_and_reason() -> None:
    invalid_pto = client.post(
        "/employees/E001/pto-adjustments",
        json={"days_delta": 0},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert invalid_pto.status_code == 422
    assert invalid_pto.json()["detail"] == "days_delta cannot be 0"

    invalid_comp = client.post(
        "/employees/E001/comp-time-adjustments",
        json={"minutes_delta": 0, "reason": ""},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert invalid_comp.status_code == 422
    assert invalid_comp.json()["detail"] == "minutes_delta cannot be 0"

    missing_reason = client.post(
        "/employees/E001/comp-time-adjustments",
        json={"minutes_delta": 15, "reason": ""},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert missing_reason.status_code == 422
    assert missing_reason.json()["detail"] == "reason is required"


def test_payroll_export_and_integration_payload(monkeypatch) -> None:
    _create_closed_shift_at(monkeypatch, datetime(2026, 5, 15, 9, 0, tzinfo=UTC), 600, employee_id="E001")
    _create_closed_shift_at(monkeypatch, datetime(2026, 5, 16, 23, 0, tzinfo=UTC), 120, employee_id="E001")
    _create_closed_shift_at(monkeypatch, datetime(2026, 5, 15, 8, 0, tzinfo=UTC), 480, employee_id="E002")

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
    assert export_body["period_start"] == "2026-01-01"
    assert export_body["period_end"] == "2026-12-31"
    assert export_body["row_count"] == 2
    assert export_body["rows"] == [
        {
            "employee_id": "E001",
            "location_id": "LOC-001",
            "total_minutes_worked": 720,
            "overtime_minutes": 120,
            "holiday_minutes": 120,
            "night_shift_minutes": 120,
        },
        {
            "employee_id": "E002",
            "location_id": "LOC-002",
            "total_minutes_worked": 480,
            "overtime_minutes": 0,
            "holiday_minutes": 0,
            "night_shift_minutes": 0,
        }
    ]

    filtered_export = client.get(
        "/companies/COMP-001/payroll-export",
        params={"period_start": "2026-05-16", "period_end": "2026-05-16"},
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-001"}),
    )
    assert filtered_export.status_code == 200
    assert filtered_export.json()["rows"] == [
        {
            "employee_id": "E001",
            "location_id": "LOC-001",
            "total_minutes_worked": 120,
            "overtime_minutes": 0,
            "holiday_minutes": 120,
            "night_shift_minutes": 120,
        },
        {
            "employee_id": "E002",
            "location_id": "LOC-002",
            "total_minutes_worked": 0,
            "overtime_minutes": 0,
            "holiday_minutes": 0,
            "night_shift_minutes": 0,
        },
    ]

    integration = client.get(
        "/companies/COMP-001/payroll-integration-payload",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-001"}),
    )
    assert integration.status_code == 200
    integration_body = integration.json()
    assert integration_body["schema_version"] == "1.0"
    assert integration_body["destination"] == "future-payroll-integration"
    assert integration_body["employees"] == export_body["rows"]


def test_location_scoped_endpoints(monkeypatch) -> None:
    _create_closed_shift(monkeypatch, duration_minutes=120)
    _create_closed_shift_at(monkeypatch, datetime(2026, 5, 15, 8, 0, tzinfo=UTC), 480, employee_id="E002")
    _create_closed_shift_at(monkeypatch, datetime(2026, 5, 16, 23, 0, tzinfo=UTC), 120, employee_id="E002")

    locations = client.get("/companies/COMP-001/locations", headers=auth_headers())
    assert locations.status_code == 200
    assert locations.json()["company_id"] == "COMP-001"
    assert locations.json()["locations"] == [
        {"location_id": "LOC-001", "employee_count": 1},
        {"location_id": "LOC-002", "employee_count": 1},
    ]

    location_employees = client.get(
        "/companies/COMP-001/locations/LOC-001/employees",
        headers=auth_headers(),
    )
    assert location_employees.status_code == 200
    assert location_employees.json()["employees"] == [
        {"employee_id": "E001", "company_id": "COMP-001", "location_id": "LOC-001"}
    ]

    second_location_employees = client.get(
        "/companies/COMP-001/locations/LOC-002/employees",
        headers=auth_headers(),
    )
    assert second_location_employees.status_code == 200
    assert second_location_employees.json()["employees"] == [
        {"employee_id": "E002", "company_id": "COMP-001", "location_id": "LOC-002"}
    ]

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
    assert body["row_count"] == 1
    assert body["rows"] == [
        {
            "employee_id": "E001",
            "location_id": "LOC-001",
            "total_minutes_worked": 120,
            "overtime_minutes": 0,
            "holiday_minutes": 0,
            "night_shift_minutes": 0,
        }
    ]

    second_allowed = client.get(
        "/companies/COMP-001/locations/LOC-002/payroll-export",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-001"}),
    )
    assert second_allowed.status_code == 200
    second_body = second_allowed.json()
    assert second_body["location_id"] == "LOC-002"
    assert second_body["row_count"] == 1
    assert second_body["rows"] == [
        {
            "employee_id": "E002",
            "location_id": "LOC-002",
            "total_minutes_worked": 600,
            "overtime_minutes": 0,
            "holiday_minutes": 120,
            "night_shift_minutes": 120,
        }
    ]

    second_filtered = client.get(
        "/companies/COMP-001/locations/LOC-002/payroll-export",
        params={"period_start": "2026-05-15", "period_end": "2026-05-15"},
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-001"}),
    )
    assert second_filtered.status_code == 200
    assert second_filtered.json()["rows"] == [
        {
            "employee_id": "E002",
            "location_id": "LOC-002",
            "total_minutes_worked": 480,
            "overtime_minutes": 0,
            "holiday_minutes": 0,
            "night_shift_minutes": 0,
        }
    ]


def test_operational_and_crosscheck_reports(monkeypatch) -> None:
    _create_closed_shift(monkeypatch, duration_minutes=120)
    _create_closed_shift_at(monkeypatch, datetime(2026, 5, 15, 8, 0, tzinfo=UTC), 480, employee_id="E002")
    _create_closed_shift_at(monkeypatch, datetime(2026, 5, 15, 7, 0, tzinfo=UTC), 60, employee_id="E101")

    report = client.get(
        "/reports/operational",
        params={"company_id": "COMP-001"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER", "x-company-id": "COMP-001"}),
    )
    assert report.status_code == 200
    report_body = report.json()
    assert report_body["company_id"] == "COMP-001"
    assert report_body["event_count"] == 4
    assert report_body["accepted_event_count"] == 4
    assert report_body["rejected_event_count"] == 0
    assert report_body["open_shift_count"] == 0
    assert report_body["closed_shift_count"] == 2

    crosscheck = client.get(
        "/reports/crosscheck",
        params={"employee_id": "E001"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert crosscheck.status_code == 200
    crosscheck_body = crosscheck.json()
    assert crosscheck_body["status"] == "MATCH"
    assert crosscheck_body["payroll_summary_total_minutes"] == 120
    assert crosscheck_body["derived_shift_total_minutes"] == 120


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


def test_company_admin_workflows_cover_location_notifications_and_secret_stubs() -> None:
    reassigned = client.patch(
        "/companies/COMP-001/employees/E001",
        json={"location_id": "LOC-002"},
        headers=auth_headers("demo-admin-token", {"x-role": "ADMIN", "x-company-id": "COMP-001"}),
    )
    assert reassigned.status_code == 200
    assert reassigned.json()["location_id"] == "LOC-002"

    locations = client.get("/companies/COMP-001/locations", headers=auth_headers())
    assert locations.status_code == 200
    assert locations.json()["locations"] == [{"location_id": "LOC-002", "employee_count": 2}]

    notification_settings = client.put(
        "/companies/COMP-001/notification-settings",
        json={
            "destination_type": "WEBHOOK",
            "target": "https://example.invalid/buildathon-webhook",
            "secret_reference": "ops/buildathon/webhook-token",
            "enabled": True,
        },
        headers=auth_headers("demo-admin-token", {"x-role": "ADMIN", "x-company-id": "COMP-001"}),
    )
    assert notification_settings.status_code == 200
    notification_body = notification_settings.json()
    assert notification_body["status"] == "CONFIGURED"
    assert notification_body["delivery_mode"] == "STUB"

    notification_test = client.post(
        "/companies/COMP-001/notification-settings/test",
        headers=auth_headers("demo-admin-token", {"x-role": "ADMIN", "x-company-id": "COMP-001"}),
    )
    assert notification_test.status_code == 200
    assert notification_test.json()["status"] == "TEST_DELIVERY_SIMULATED"

    secret_provider = client.put(
        "/companies/COMP-001/secret-provider",
        json={"provider": "VAULT_STUB", "reference_name": "kv/buildathon/payroll", "enabled": True},
        headers=auth_headers("demo-admin-token", {"x-role": "ADMIN", "x-company-id": "COMP-001"}),
    )
    assert secret_provider.status_code == 200
    secret_body = secret_provider.json()
    assert secret_body["provider"] == "VAULT_STUB"
    assert secret_body["status"] == "CONFIGURED"
    assert secret_body["stores_secret_material"] is False


def test_compliance_report_fails_for_missing_punch_and_long_shift(monkeypatch) -> None:
    started_at = datetime(2026, 5, 15, 9, 0, tzinfo=UTC)
    monkeypatch.setattr(main, "utc_now", lambda: started_at)
    assert client.post("/employees/E001/clock-in", headers=auth_headers()).status_code == 200

    monkeypatch.setattr(main, "utc_now", lambda: started_at + timedelta(minutes=780))

    response = client.get("/employees/E001/compliance-report", headers=auth_headers())

    assert response.status_code == 200
    body = response.json()
    assert body["tax_validation_status"] == "WARN"
    assert body["labor_rule_validation_status"] == "FAIL"
    assert body["attendance_exception_count"] == 1
    labor_rules = {item["rule"]: item for item in body["labor_rule_validations"]}
    assert labor_rules["ATTENDANCE_EXCEPTIONS_CLEAR"]["status"] == "FAIL"
    assert labor_rules["NO_OPEN_SHIFT_PENDING"]["status"] == "FAIL"
    assert labor_rules["MAX_SHIFT_DURATION_UNDER_12_HOURS"]["status"] == "PASS"
