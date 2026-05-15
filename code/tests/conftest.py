import os
import sys

import pytest

# Allow `from backend.main import app` without requiring manual PYTHONPATH export.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def reset_state() -> None:
    import backend.main as main
    from backend.db import Base, SessionLocal, engine
    from backend.models import Employee, PolicySetting

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    main.REQUEST_METRICS = main._new_request_metrics()

    db = SessionLocal()
    try:
        db.add_all(
            [
                Employee(employee_id="E001", company_id="COMP-001", location_id="LOC-001"),
                Employee(employee_id="E002", company_id="COMP-001", location_id="LOC-002"),
                Employee(employee_id="E101", company_id="COMP-002", location_id="LOC-101"),
            ]
        )
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
