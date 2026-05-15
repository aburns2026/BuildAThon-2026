import json
import os
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

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


def test_docker_compose_stack_starts_and_serves_health() -> None:
    env = os.environ.copy()

    subprocess.run(["docker", "compose", "config"], cwd=REPO_ROOT, check=True, env=env)
    try:
        subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=REPO_ROOT, check=True, env=env)

        health_status, health_body = _wait_for_http("http://127.0.0.1:8000/health")
        frontend_status, frontend_body = _wait_for_http("http://127.0.0.1:4173/")
        health_payload = json.loads(health_body)

        assert health_status == 200
        assert health_payload["status"] == "ok"
        assert health_payload["database"]["status"] == "ok"
        assert frontend_status == 200
        assert "<html" in frontend_body.lower()
        assert "Workforce Time Tracking & Payroll Integration Platform" in frontend_body
    finally:
        subprocess.run(["docker", "compose", "down"], cwd=REPO_ROOT, check=False, env=env)