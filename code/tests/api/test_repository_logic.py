from datetime import UTC, datetime, timedelta

from backend.db import SessionLocal
from backend.main import _build_compliance_report
from backend.models import Employee, Shift
from backend.repositories import compute_night_minutes, is_holiday_shift, payroll_metrics


def _create_closed_shift(
    *,
    employee_id: str = "E001",
    start_at: datetime,
    duration_minutes: int,
) -> None:
    db = SessionLocal()
    try:
        end_at = start_at + timedelta(minutes=duration_minutes)
        db.add(
            Shift(
                shift_id=f"shift-{employee_id}-{start_at.isoformat()}",
                employee_id=employee_id,
                start_at=start_at,
                end_at=end_at,
                duration_minutes=duration_minutes,
                state="CLOSED",
            )
        )
        db.commit()
    finally:
        db.close()


def test_compute_night_minutes_respects_start_and_end_boundaries() -> None:
    evening_start = datetime(2026, 5, 18, 21, 0, tzinfo=UTC)
    assert compute_night_minutes(evening_start, evening_start + timedelta(hours=1)) == 0
    assert compute_night_minutes(evening_start, evening_start + timedelta(hours=2)) == 60

    early_morning_start = datetime(2026, 5, 19, 5, 0, tzinfo=UTC)
    assert compute_night_minutes(early_morning_start, early_morning_start + timedelta(hours=2)) == 60


def test_is_holiday_shift_only_marks_weekend_dates() -> None:
    friday = datetime(2026, 5, 15, 9, 0, tzinfo=UTC)
    saturday = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)

    assert is_holiday_shift(friday) is False
    assert is_holiday_shift(saturday) is True


def test_payroll_metrics_roll_up_overtime_holiday_and_night_minutes() -> None:
    _create_closed_shift(start_at=datetime(2026, 5, 15, 9, 0, tzinfo=UTC), duration_minutes=600)
    _create_closed_shift(start_at=datetime(2026, 5, 16, 23, 0, tzinfo=UTC), duration_minutes=120)

    db = SessionLocal()
    try:
        metrics = payroll_metrics(db, "E001")
    finally:
        db.close()

    assert metrics["closed_shift_count"] == 2
    assert metrics["total_minutes"] == 720
    assert metrics["overtime_minutes"] == 120
    assert metrics["holiday_minutes"] == 120
    assert metrics["night_shift_minutes"] == 120


def test_payroll_metrics_respect_boundary_values_across_multiple_shifts() -> None:
    _create_closed_shift(start_at=datetime(2026, 5, 15, 8, 0, tzinfo=UTC), duration_minutes=480)
    _create_closed_shift(start_at=datetime(2026, 5, 16, 22, 0, tzinfo=UTC), duration_minutes=481)
    _create_closed_shift(start_at=datetime(2026, 5, 18, 6, 0, tzinfo=UTC), duration_minutes=30)

    db = SessionLocal()
    try:
        metrics = payroll_metrics(db, "E001")
    finally:
        db.close()

    assert metrics["closed_shift_count"] == 3
    assert metrics["total_minutes"] == 991
    assert metrics["overtime_minutes"] == 1
    assert metrics["holiday_minutes"] == 481
    assert metrics["night_shift_minutes"] == 480


def test_compliance_report_warns_when_no_taxable_time_exists() -> None:
    db = SessionLocal()
    try:
        report = _build_compliance_report(db, "E001")
    finally:
        db.close()

    tax_rules = {item["rule"]: item for item in report["tax_validations"]}
    labor_rules = {item["rule"]: item for item in report["labor_rule_validations"]}

    assert report["tax_validation_status"] == "WARN"
    assert tax_rules["TAXABLE_TIME_PRESENT"]["status"] == "WARN"
    assert labor_rules["NO_OPEN_SHIFT_PENDING"]["status"] == "PASS"


def test_compliance_report_fails_org_assignment_and_long_shift_boundaries() -> None:
    _create_closed_shift(start_at=datetime(2026, 5, 15, 8, 0, tzinfo=UTC), duration_minutes=721)

    db = SessionLocal()
    try:
        employee = db.get(Employee, "E001")
        assert employee is not None
        employee.company_id = ""
        db.commit()

        report = _build_compliance_report(db, "E001")
    finally:
        db.close()

    tax_rules = {item["rule"]: item for item in report["tax_validations"]}
    labor_rules = {item["rule"]: item for item in report["labor_rule_validations"]}

    assert report["tax_validation_status"] == "FAIL"
    assert report["labor_rule_validation_status"] == "FAIL"
    assert tax_rules["EMPLOYEE_ORG_ASSIGNMENT_PRESENT"]["status"] == "FAIL"
    assert labor_rules["MAX_SHIFT_DURATION_UNDER_12_HOURS"]["status"] == "FAIL"


def test_compliance_report_allows_exact_twelve_hour_shift_boundary() -> None:
    _create_closed_shift(start_at=datetime(2026, 5, 15, 8, 0, tzinfo=UTC), duration_minutes=720)

    db = SessionLocal()
    try:
        report = _build_compliance_report(db, "E001")
    finally:
        db.close()

    labor_rules = {item["rule"]: item for item in report["labor_rule_validations"]}

    assert report["labor_rule_validation_status"] == "PASS"
    assert labor_rules["MAX_SHIFT_DURATION_UNDER_12_HOURS"]["status"] == "PASS"


def test_compliance_report_fails_when_open_shift_is_pending_even_with_taxable_time() -> None:
    _create_closed_shift(start_at=datetime(2026, 5, 15, 8, 0, tzinfo=UTC), duration_minutes=480)

    db = SessionLocal()
    try:
        db.add(
            Shift(
                shift_id="shift-open-boundary",
                employee_id="E001",
                start_at=datetime.now(UTC),
                end_at=None,
                duration_minutes=None,
                state="OPEN",
            )
        )
        db.commit()

        report = _build_compliance_report(db, "E001")
    finally:
        db.close()

    tax_rules = {item["rule"]: item for item in report["tax_validations"]}
    labor_rules = {item["rule"]: item for item in report["labor_rule_validations"]}

    assert tax_rules["TAXABLE_TIME_PRESENT"]["status"] == "PASS"
    assert report["labor_rule_validation_status"] == "FAIL"
    assert labor_rules["NO_OPEN_SHIFT_PENDING"]["status"] == "FAIL"