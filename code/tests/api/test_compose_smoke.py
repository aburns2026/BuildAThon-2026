import json
import os
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[3]


def _wait_for_http(url: str, timeout_seconds: int = 90) -> tuple[int, str]:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except (URLError, OSError, ConnectionError) as exc:
            last_error = str(exc)
        time.sleep(1)
    raise AssertionError(f"Timed out waiting for {url}: {last_error}")


def _json_request(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, body: dict | None = None) -> tuple[int, dict]:
    encoded_body = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        url,
        data=encoded_body,
        headers={"Content-Type": "application/json", **(headers or {})},
        method=method,
    )
    with urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return response.status, payload


def test_docker_compose_stack_starts_and_serves_health() -> None:
    env = os.environ.copy()

    subprocess.run(["docker", "compose", "config"], cwd=REPO_ROOT, check=True, env=env)
    subprocess.run(["docker", "compose", "down", "-v", "--remove-orphans"], cwd=REPO_ROOT, check=False, env=env)
    try:
        subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=REPO_ROOT, check=True, env=env)

        health_status, health_body = _wait_for_http("http://127.0.0.1:8000/health")
        frontend_status, frontend_body = _wait_for_http("http://127.0.0.1:4173/")
        health_payload = json.loads(health_body)

        clock_in_status, clock_in_body = _json_request(
            "http://127.0.0.1:8000/employees/E001/clock-in",
            method="POST",
            headers={"Authorization": "Bearer demo-employee-token"},
        )
        clock_out_status, clock_out_body = _json_request(
            "http://127.0.0.1:8000/employees/E001/clock-out",
            method="POST",
            headers={"Authorization": "Bearer demo-employee-token"},
        )
        shifts_status, shifts_body = _json_request(
            "http://127.0.0.1:8000/employees/E001/shifts",
            headers={"Authorization": "Bearer demo-employee-token"},
        )
        export_status, export_body = _json_request(
            "http://127.0.0.1:8000/companies/COMP-001/payroll-export",
            headers={
                "Authorization": "Bearer demo-payroll-token",
                "x-role": "PAYROLL",
                "x-company-id": "COMP-001",
            },
        )
        shift_date = str(clock_out_body["clock_out_at"]).split("T", 1)[0]
        filtered_export_status, filtered_export_body = _json_request(
            f"http://127.0.0.1:8000/companies/COMP-001/payroll-export?period_start={shift_date}&period_end={shift_date}",
            headers={
                "Authorization": "Bearer demo-payroll-token",
                "x-role": "PAYROLL",
                "x-company-id": "COMP-001",
            },
        )

        assert health_status == 200
        assert health_payload["status"] == "ok"
        assert health_payload["database"]["status"] == "ok"
        assert frontend_status == 200
        assert "<html" in frontend_body.lower()
        assert "Workforce Time Tracking & Payroll Integration Platform" in frontend_body
        assert clock_in_status == 200
        assert clock_in_body["employee_id"] == "E001"
        assert clock_in_body["status"] == "CLOCKED_IN"
        assert clock_out_status == 200
        assert clock_out_body["employee_id"] == "E001"
        assert clock_out_body["status"] == "CLOCKED_OUT"
        assert shifts_status == 200
        assert len(shifts_body["shifts"]) == 1
        assert shifts_body["shifts"][0]["employee_id"] == "E001"
        assert shifts_body["shifts"][0]["state"] == "CLOSED"
        assert export_status == 200
        assert export_body["company_id"] == "COMP-001"
        assert export_body["row_count"] == 2
        assert export_body["rows"][0]["employee_id"] == "E001"
        assert export_body["rows"][1]["employee_id"] == "E002"
        assert filtered_export_status == 200
        assert filtered_export_body["period_start"] == shift_date
        assert filtered_export_body["period_end"] == shift_date
        assert filtered_export_body["rows"][0]["employee_id"] == "E001"
        assert filtered_export_body["rows"][0]["total_minutes_worked"] >= 0
        assert filtered_export_body["rows"][1] == {
            "employee_id": "E002",
            "location_id": "LOC-002",
            "total_minutes_worked": 0,
            "overtime_minutes": 0,
            "holiday_minutes": 0,
            "night_shift_minutes": 0,
        }
    finally:
        subprocess.run(["docker", "compose", "down", "-v", "--remove-orphans"], cwd=REPO_ROOT, check=False, env=env)