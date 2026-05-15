from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def auth_headers(token: str = "demo-employee-token", extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if extra:
        headers.update(extra)
    return headers


def test_create_and_list_time_corrections() -> None:
    created = client.post(
        "/employees/E001/time-corrections",
        json={"reason": "Forgot to clock out"},
        headers=auth_headers(),
    )
    assert created.status_code == 200

    listed = client.get("/employees/E001/time-corrections", headers=auth_headers())
    assert listed.status_code == 200
    assert len(listed.json()["time_corrections"]) == 1


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
    assert balance.json()["used_days"] == 1


def test_schedule_shift_and_list() -> None:
    created = client.post(
        "/employees/E001/scheduled-shifts",
        json={"start_at": "2026-05-15T09:00:00+00:00", "end_at": "2026-05-15T17:00:00+00:00"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert created.status_code == 200

    listed = client.get("/employees/E001/scheduled-shifts", headers=auth_headers())
    assert listed.status_code == 200
    assert len(listed.json()["scheduled_shifts"]) == 1


def test_payroll_breakdown_and_compliance_report() -> None:
    assert client.post("/employees/E001/clock-in", headers=auth_headers()).status_code == 200
    assert client.post("/employees/E001/clock-out", headers=auth_headers()).status_code == 200

    breakdown = client.get("/employees/E001/payroll-breakdown", headers=auth_headers())
    assert breakdown.status_code == 200
    assert "overtime_minutes" in breakdown.json()

    compliance = client.get("/employees/E001/compliance-report", headers=auth_headers())
    assert compliance.status_code == 200
    compliance_body = compliance.json()
    assert compliance_body["tax_validation_status"] == "PASS"
    assert compliance_body["labor_rule_validation_status"] == "PASS"
    assert len(compliance_body["tax_validations"]) >= 1
    assert len(compliance_body["labor_rule_validations"]) >= 1


def test_company_listing_and_ops_diagnostics() -> None:
    company = client.get("/companies/COMP-001/employees", headers=auth_headers())
    assert company.status_code == 200
    assert len(company.json()["employees"]) == 1

    diagnostics = client.get("/ops/diagnostics", headers=auth_headers())
    assert diagnostics.status_code == 200
    body = diagnostics.json()
    assert "audit_event_count" in body
    assert body["database_status"] == "ok"
    assert body["database_backend"]
    assert body["request_count_total"] >= 1
