import os
import sys

import pytest

# Allow `from backend.main import app` without requiring manual PYTHONPATH export.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def reset_state() -> None:
    from backend.db import Base, SessionLocal, engine
    from backend.main import COMP_TIME_ADJUSTMENTS, POLICY_CONFIG, PTO_ADJUSTMENTS, TIME_CORRECTIONS
    from backend.models import Employee

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        db.add(Employee(employee_id="E001", company_id="COMP-001", location_id="LOC-001"))
        db.commit()
    finally:
        db.close()

    TIME_CORRECTIONS.clear()
    COMP_TIME_ADJUSTMENTS.clear()
    PTO_ADJUSTMENTS.clear()
    POLICY_CONFIG.clear()
    POLICY_CONFIG.update({"minimum_break_minutes": 30, "core_hour_start": 10, "core_hour_end": 15})
