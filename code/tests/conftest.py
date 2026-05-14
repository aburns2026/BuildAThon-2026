import os
import sys

import pytest

# Allow `from backend.main import app` without requiring manual PYTHONPATH export.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def reset_state() -> None:
    from backend.db import Base, SessionLocal, engine
    from backend.models import Employee, PolicySetting

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        db.add(Employee(employee_id="E001", company_id="COMP-001", location_id="LOC-001"))
        db.add_all(
            [
                PolicySetting(policy_key="minimum_break_minutes", int_value=30),
                PolicySetting(policy_key="core_hour_start", int_value=10),
                PolicySetting(policy_key="core_hour_end", int_value=15),
            ]
        )
        db.commit()
    finally:
        db.close()
