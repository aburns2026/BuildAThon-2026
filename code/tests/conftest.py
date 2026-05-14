import os
import sys

import pytest

# Allow `from backend.main import app` without requiring manual PYTHONPATH export.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def reset_in_memory_state() -> None:
	from backend.main import AUDIT_EVENTS, OPEN_SHIFTS, SHIFTS

	OPEN_SHIFTS.clear()
	SHIFTS.clear()
	AUDIT_EVENTS.clear()
