from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def auth_headers(token: str = "demo-employee-token", extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if extra:
        headers.update(extra)
    return headers


def test_non_health_endpoints_require_authorization_header() -> None:
    response = client.get("/employees/E001/shifts")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing Authorization header"


def test_invalid_bearer_token_rejected() -> None:
    response = client.get("/employees/E001/shifts", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid bearer token"


def test_role_header_spoof_rejected_when_principal_mismatch() -> None:
    response = client.post(
        "/employees/E001/scheduled-shifts",
        json={"start_at": "2026-05-15T09:00:00+00:00", "end_at": "2026-05-15T17:00:00+00:00"},
        headers=auth_headers("demo-employee-token", {"x-role": "MANAGER"}),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "x-role does not match authenticated principal"


def test_invalid_employee_id_format_rejected() -> None:
    response = client.post("/employees/not-valid/clock-in", headers=auth_headers())

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid employee_id format"


def test_time_correction_reason_length_limited() -> None:
    response = client.post(
        "/employees/E001/time-corrections",
        json={"reason": "x" * 201},
        headers=auth_headers(),
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "reason exceeds 200 characters"


def test_leave_request_date_validation() -> None:
    response = client.post(
        "/employees/E001/leave-requests",
        json={"start_date": "bad-date", "end_date": "2026-05-20"},
        headers=auth_headers(),
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "start_date must be ISO date (YYYY-MM-DD)"


def test_leave_request_date_order_validation() -> None:
    response = client.post(
        "/employees/E001/leave-requests",
        json={"start_date": "2026-05-21", "end_date": "2026-05-20"},
        headers=auth_headers(),
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "end_date must be on or after start_date"


def test_scheduled_shift_datetime_and_order_validation() -> None:
    invalid = client.post(
        "/employees/E001/scheduled-shifts",
        json={"start_at": "not-datetime", "end_at": "2026-05-15T17:00:00+00:00"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert invalid.status_code == 422
    assert invalid.json()["detail"] == "start_at must be ISO datetime"

    reversed_window = client.post(
        "/employees/E001/scheduled-shifts",
        json={"start_at": "2026-05-15T17:00:00+00:00", "end_at": "2026-05-15T09:00:00+00:00"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert reversed_window.status_code == 422
    assert reversed_window.json()["detail"] == "end_at must be after start_at"


def test_company_scoped_endpoints_require_company_claim_header() -> None:
    export_missing = client.get(
        "/companies/COMP-001/payroll-export",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL"}),
    )
    assert export_missing.status_code == 403
    assert export_missing.json()["detail"] == "Missing x-company-id header"

    integration_missing = client.get(
        "/companies/COMP-001/payroll-integration-payload",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL"}),
    )
    assert integration_missing.status_code == 403
    assert integration_missing.json()["detail"] == "Missing x-company-id header"

    location_export_missing = client.get(
        "/companies/COMP-001/locations/LOC-001/payroll-export",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL"}),
    )
    assert location_export_missing.status_code == 403
    assert location_export_missing.json()["detail"] == "Missing x-company-id header"


def test_company_scoped_endpoints_reject_mismatched_company_claim() -> None:
    export_mismatch = client.get(
        "/companies/COMP-001/payroll-export",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-999"}),
    )
    assert export_mismatch.status_code == 403
    assert export_mismatch.json()["detail"] == "Company mismatch"

    integration_mismatch = client.get(
        "/companies/COMP-001/payroll-integration-payload",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-999"}),
    )
    assert integration_mismatch.status_code == 403
    assert integration_mismatch.json()["detail"] == "Company mismatch"

    location_export_mismatch = client.get(
        "/companies/COMP-001/locations/LOC-001/payroll-export",
        headers=auth_headers("demo-payroll-token", {"x-role": "PAYROLL", "x-company-id": "COMP-999"}),
    )
    assert location_export_mismatch.status_code == 403
    assert location_export_mismatch.json()["detail"] == "Company mismatch"


def test_operational_report_company_filter_requires_matching_claim() -> None:
    missing_claim = client.get(
        "/reports/operational",
        params={"company_id": "COMP-001"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER"}),
    )
    assert missing_claim.status_code == 403
    assert missing_claim.json()["detail"] == "Missing x-company-id header"

    mismatch_claim = client.get(
        "/reports/operational",
        params={"company_id": "COMP-001"},
        headers=auth_headers("demo-manager-token", {"x-role": "MANAGER", "x-company-id": "COMP-999"}),
    )
    assert mismatch_claim.status_code == 403
    assert mismatch_claim.json()["detail"] == "Company mismatch"
