import os
from datetime import UTC, datetime
from datetime import date as date_cls
import logging
import re
from time import perf_counter
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session

try:
    from .db import Base, SessionLocal, engine, get_database_health, get_database_runtime_info, get_db, init_db
    from .models import AuditEvent, CompTimeAdjustment, Employee, LeaveRequest, NotificationEndpoint, PolicySetting, PtoAdjustment, ScheduledShift, SecretProviderConfig, Shift, TimeCorrection
    from .repositories import (
        add_audit_event,
        comp_time_adjustment_to_dict,
        ensure_seed_employee,
        event_to_dict,
        get_open_shift,
        leave_request_to_dict,
        list_closed_shifts,
        payroll_metrics,
        scheduled_shift_to_dict,
        shift_to_dict,
        time_correction_to_dict,
        utc_now,
        utc_now_iso,
    )
except ImportError:
    from db import Base, SessionLocal, engine, get_database_health, get_database_runtime_info, get_db, init_db
    from models import AuditEvent, CompTimeAdjustment, Employee, LeaveRequest, NotificationEndpoint, PolicySetting, PtoAdjustment, ScheduledShift, SecretProviderConfig, Shift, TimeCorrection
    from repositories import (
        add_audit_event,
        comp_time_adjustment_to_dict,
        ensure_seed_employee,
        event_to_dict,
        get_open_shift,
        leave_request_to_dict,
        list_closed_shifts,
        payroll_metrics,
        scheduled_shift_to_dict,
        shift_to_dict,
        time_correction_to_dict,
        utc_now,
        utc_now_iso,
    )


EMPLOYEE_ID_PATTERN = re.compile(r"^E[0-9]{3,10}$")
LOG_LEVEL = "INFO"
REQUEST_ID_HEADER = "x-request-id"
TEST_SUPPORT_TOKEN_HEADER = "x-test-support-token"
TEST_SUPPORT_TOKEN = os.getenv("TEST_SUPPORT_TOKEN", "buildathon-e2e")
DEMO_RESET_TOKEN_HEADER = "x-demo-reset-token"

if not logging.getLogger().handlers:
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

logger = logging.getLogger("buildathon.api")
APP_STARTED_AT = utc_now()
def _new_request_metrics() -> dict[str, object]:
    return {
        "request_count_total": 0,
        "request_error_count": 0,
        "request_duration_ms_sum": 0,
        "request_duration_ms_max": 0,
        "requests_by_path": {},
        "requests_by_status": {},
    }


REQUEST_METRICS: dict[str, object] = _new_request_metrics()

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "EMPLOYEE": {"clock_in", "clock_out", "view_self"},
    "MANAGER": {
        "clock_in",
        "clock_out",
        "view_self",
        "approve_leave",
        "schedule_shift",
        "adjust_balances",
        "view_reports",
    },
    "PAYROLL": {"view_self", "payroll_export", "payroll_integration", "adjust_balances", "view_reports"},
    "ADMIN": {
        "clock_in",
        "clock_out",
        "view_self",
        "approve_leave",
        "schedule_shift",
        "adjust_balances",
        "view_reports",
        "payroll_export",
        "payroll_integration",
        "policy_configure",
    },
}

DEFAULT_POLICY_CONFIG: dict[str, int] = {
    "minimum_break_minutes": 30,
    "core_hour_start": 10,
    "core_hour_end": 15,
}

ALLOWED_NOTIFICATION_DESTINATIONS = {"WEBHOOK", "EMAIL", "SLACK_STUB"}
ALLOWED_SECRET_PROVIDERS = {"ENV", "VAULT_STUB", "KMS_STUB"}

AUTH_PRINCIPALS: dict[str, dict[str, str]] = {
    "demo-employee-token": {"role": "EMPLOYEE", "company_id": "COMP-001"},
    "demo-manager-token": {"role": "MANAGER", "company_id": "COMP-001"},
    "demo-payroll-token": {"role": "PAYROLL", "company_id": "COMP-001"},
    "demo-admin-token": {"role": "ADMIN", "company_id": "COMP-001"},
}

AUTH_EXEMPT_PATH_PREFIXES = (
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/demo-support",
    "/test-support",
)

ALLOWED_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def _uptime_seconds() -> int:
    return max(0, int((utc_now() - APP_STARTED_AT).total_seconds()))


def _metric_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _record_request_metric(method: str, path: str, status_code: int, duration_ms: int, *, failed: bool) -> None:
    REQUEST_METRICS["request_count_total"] = int(REQUEST_METRICS["request_count_total"]) + 1
    if failed:
        REQUEST_METRICS["request_error_count"] = int(REQUEST_METRICS["request_error_count"]) + 1
    REQUEST_METRICS["request_duration_ms_sum"] = int(REQUEST_METRICS["request_duration_ms_sum"]) + duration_ms
    REQUEST_METRICS["request_duration_ms_max"] = max(int(REQUEST_METRICS["request_duration_ms_max"]), duration_ms)

    requests_by_path = REQUEST_METRICS["requests_by_path"]
    if not isinstance(requests_by_path, dict):
        requests_by_path = {}
        REQUEST_METRICS["requests_by_path"] = requests_by_path
    path_key = f"{method} {path}"
    requests_by_path[path_key] = int(requests_by_path.get(path_key, 0)) + 1

    requests_by_status = REQUEST_METRICS["requests_by_status"]
    if not isinstance(requests_by_status, dict):
        requests_by_status = {}
        REQUEST_METRICS["requests_by_status"] = requests_by_status
    status_key = str(status_code)
    requests_by_status[status_key] = int(requests_by_status.get(status_key, 0)) + 1


def get_policy_values(db: Session) -> dict[str, int]:
    stored = {
        item.policy_key: int(item.int_value)
        for item in db.query(PolicySetting).filter(PolicySetting.policy_key.in_(DEFAULT_POLICY_CONFIG.keys())).all()
    }
    return {**DEFAULT_POLICY_CONFIG, **stored}


def ensure_policy_settings(db: Session) -> dict[str, int]:
    existing_keys = {
        item.policy_key
        for item in db.query(PolicySetting.policy_key).filter(PolicySetting.policy_key.in_(DEFAULT_POLICY_CONFIG.keys())).all()
    }
    created = False
    for key, value in DEFAULT_POLICY_CONFIG.items():
        if key not in existing_keys:
            db.add(PolicySetting(policy_key=key, int_value=value))
            created = True
    if created:
        db.commit()
    return get_policy_values(db)


def save_policy_values(db: Session, values: dict[str, int]) -> dict[str, int]:
    ensure_policy_settings(db)
    for key, value in values.items():
        item = db.get(PolicySetting, key)
        if item is None:
            db.add(PolicySetting(policy_key=key, int_value=value))
        else:
            item.int_value = value
    db.commit()
    return get_policy_values(db)


def _notification_endpoint_to_dict(item: NotificationEndpoint | None, company_id: str) -> dict:
    if item is None:
        return {
            "company_id": company_id,
            "destination_type": "WEBHOOK",
            "target": "",
            "secret_reference": None,
            "enabled": False,
            "status": "NOT_CONFIGURED",
            "last_tested_at": None,
            "delivery_mode": "STUB",
        }
    return {
        "company_id": item.company_id,
        "destination_type": item.destination_type,
        "target": item.target,
        "secret_reference": item.secret_reference,
        "enabled": bool(item.enabled),
        "status": item.status,
        "last_tested_at": item.last_tested_at.isoformat() if item.last_tested_at else None,
        "delivery_mode": "STUB",
    }


def _secret_provider_to_dict(item: SecretProviderConfig | None, company_id: str) -> dict:
    if item is None:
        return {
            "company_id": company_id,
            "provider": "ENV",
            "reference_name": "",
            "enabled": False,
            "status": "NOT_CONFIGURED",
            "stores_secret_material": False,
            "updated_at": None,
        }
    return {
        "company_id": item.company_id,
        "provider": item.provider,
        "reference_name": item.reference_name,
        "enabled": bool(item.enabled),
        "status": item.status,
        "stores_secret_material": False,
        "updated_at": item.updated_at.isoformat(),
    }


def reset_application_state() -> None:
    global REQUEST_METRICS

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    REQUEST_METRICS = _new_request_metrics()

    db = SessionLocal()
    try:
        ensure_seed_employee(db)
        ensure_policy_settings(db)
    finally:
        db.close()


def test_support_enabled() -> bool:
    return os.getenv("ENABLE_TEST_SUPPORT_ENDPOINTS", "0") == "1"


def demo_reset_enabled() -> bool:
    return os.getenv("ENABLE_DEMO_RESET_ENDPOINTS", "0") == "1"


def demo_reset_on_startup_enabled() -> bool:
    return os.getenv("RESET_DATABASE_ON_STARTUP", "0") == "1"


def demo_reset_token() -> str:
    return os.getenv("DEMO_RESET_TOKEN", "buildathon-demo-reset")


def bootstrap_application_state() -> None:
    init_db()
    if demo_reset_on_startup_enabled():
        reset_application_state()
        return

    db = next(get_db())
    try:
        ensure_seed_employee(db)
        ensure_policy_settings(db)
    finally:
        db.close()

def validate_employee_id_format(employee_id: str) -> None:
    if not EMPLOYEE_ID_PATTERN.match(employee_id):
        raise HTTPException(status_code=422, detail="Invalid employee_id format")


def parse_iso_date(value: str, field_name: str) -> date_cls:
    try:
        return date_cls.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"{field_name} must be ISO date (YYYY-MM-DD)") from exc


def parse_iso_datetime(value: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"{field_name} must be ISO datetime") from exc


def parse_optional_iso_date(value: str | None, field_name: str) -> date_cls | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return parse_iso_date(stripped, field_name)


def ensure_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def employee_exists(db: Session, employee_id: str) -> bool:
    return db.get(Employee, employee_id) is not None


def ensure_employee_exists(db: Session, employee_id: str) -> None:
    validate_employee_id_format(employee_id)
    if not employee_exists(db, employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")


def resolve_auth_principal(request: Request) -> dict[str, str]:
    auth_header = request.headers.get("authorization", "").strip()
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    principal = AUTH_PRINCIPALS.get(token.strip())
    if principal is None:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    return principal


def get_effective_role(request: Request) -> str:
    principal = getattr(request.state, "auth_principal", None)
    if principal is None:
        raise HTTPException(status_code=401, detail="Unauthenticated request")

    role = principal["role"]
    requested_role = request.headers.get("x-role", "").strip().upper()
    if requested_role and requested_role != role:
        raise HTTPException(status_code=403, detail="x-role does not match authenticated principal")
    return role


def require_action(request: Request, action: str) -> str:
    role = get_effective_role(request)
    if action not in ROLE_PERMISSIONS.get(role, set()):
        raise HTTPException(status_code=403, detail=f"Role {role} is not allowed to perform action {action}")
    return role


def require_company_access(request: Request, company_id: str) -> str:
    company_claim = request.headers.get("x-company-id", "").strip()
    if not company_claim:
        raise HTTPException(status_code=403, detail="Missing x-company-id header")
    if company_claim != company_id:
        raise HTTPException(status_code=403, detail="Company mismatch")
    return company_claim


def _get_closed_shift_query(db: Session, employee_id: str):
    return (
        db.query(Shift)
        .filter(Shift.employee_id == employee_id, Shift.state == "CLOSED")
        .order_by(Shift.start_at)
    )


def _approved_leave_day_total(db: Session, employee_id: str) -> int:
    approved_requests = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.employee_id == employee_id, LeaveRequest.status == "APPROVED")
        .all()
    )
    total_days = 0
    for item in approved_requests:
        start_date = parse_iso_date(item.start_date, "start_date")
        end_date = parse_iso_date(item.end_date, "end_date")
        total_days += (end_date - start_date).days + 1
    return total_days


def _roll_up_validation_status(items: list[dict]) -> str:
    if any(item["status"] == "FAIL" for item in items):
        return "FAIL"
    if any(item["status"] == "WARN" for item in items):
        return "WARN"
    return "PASS"


def _build_compliance_report(db: Session, employee_id: str) -> dict:
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    attendance_exceptions = get_attendance_exceptions(employee_id, threshold_minutes=60, db=db)["exceptions"]
    closed_shifts = list_closed_shifts(db, employee_id)
    open_shift = get_open_shift(db, employee_id)
    payroll_summary = get_payroll_summary(employee_id, db=db)
    derived_total = sum(int(item.duration_minutes or 0) for item in closed_shifts)

    tax_validations = [
        {
            "rule": "EMPLOYEE_ORG_ASSIGNMENT_PRESENT",
            "status": "PASS" if employee.company_id and employee.location_id else "FAIL",
            "details": "Employee has required company and location assignment"
            if employee.company_id and employee.location_id
            else "Employee is missing company_id or location_id",
        },
        {
            "rule": "PAYROLL_TOTAL_RECONCILES",
            "status": "PASS" if payroll_summary["total_minutes_worked"] == derived_total else "FAIL",
            "details": "Payroll summary matches derived closed-shift total"
            if payroll_summary["total_minutes_worked"] == derived_total
            else "Payroll summary does not match derived closed-shift total",
        },
        {
            "rule": "TAXABLE_TIME_PRESENT",
            "status": "PASS" if payroll_summary["closed_shift_count"] > 0 else "WARN",
            "details": "Closed shifts are available for taxable time review"
            if payroll_summary["closed_shift_count"] > 0
            else "No closed shifts are available for taxable time review",
        },
    ]

    excessive_shifts = [shift for shift in closed_shifts if int(shift.duration_minutes or 0) > 720]
    labor_validations = [
        {
            "rule": "ATTENDANCE_EXCEPTIONS_CLEAR",
            "status": "PASS" if not attendance_exceptions else "FAIL",
            "details": "No attendance exceptions were detected"
            if not attendance_exceptions
            else f"{len(attendance_exceptions)} attendance exception(s) detected",
        },
        {
            "rule": "NO_OPEN_SHIFT_PENDING",
            "status": "PASS" if open_shift is None else "FAIL",
            "details": "No open shift is pending"
            if open_shift is None
            else "An open shift is still pending closure",
        },
        {
            "rule": "MAX_SHIFT_DURATION_UNDER_12_HOURS",
            "status": "PASS" if not excessive_shifts else "FAIL",
            "details": "All closed shifts are at or below 12 hours"
            if not excessive_shifts
            else f"{len(excessive_shifts)} shift(s) exceed 12 hours",
        },
    ]

    return {
        "employee_id": employee_id,
        "tax_validation_status": _roll_up_validation_status(tax_validations),
        "labor_rule_validation_status": _roll_up_validation_status(labor_validations),
        "attendance_exception_count": len(attendance_exceptions),
        "tax_validations": tax_validations,
        "labor_rule_validations": labor_validations,
    }


def _build_company_payroll_rows(
    db: Session,
    company_id: str,
    *,
    period_start: date_cls | None = None,
    period_end: date_cls | None = None,
) -> list[dict]:
    company_employees = (
        db.query(Employee)
        .filter(Employee.company_id == company_id)
        .order_by(Employee.employee_id)
        .all()
    )
    rows: list[dict] = []
    for employee in company_employees:
        metrics = payroll_metrics(db, employee.employee_id, period_start=period_start, period_end=period_end)
        rows.append(
            {
                "employee_id": employee.employee_id,
                "location_id": employee.location_id,
                "total_minutes_worked": metrics["total_minutes"],
                "overtime_minutes": metrics["overtime_minutes"],
                "holiday_minutes": metrics["holiday_minutes"],
                "night_shift_minutes": metrics["night_shift_minutes"],
            }
        )
    return rows


def _build_location_payroll_rows(
    db: Session,
    company_id: str,
    location_id: str,
    *,
    period_start: date_cls | None = None,
    period_end: date_cls | None = None,
) -> list[dict]:
    location_employees = (
        db.query(Employee)
        .filter(Employee.company_id == company_id, Employee.location_id == location_id)
        .order_by(Employee.employee_id)
        .all()
    )
    rows: list[dict] = []
    for employee in location_employees:
        metrics = payroll_metrics(db, employee.employee_id, period_start=period_start, period_end=period_end)
        rows.append(
            {
                "employee_id": employee.employee_id,
                "location_id": employee.location_id,
                "total_minutes_worked": metrics["total_minutes"],
                "overtime_minutes": metrics["overtime_minutes"],
                "holiday_minutes": metrics["holiday_minutes"],
                "night_shift_minutes": metrics["night_shift_minutes"],
            }
        )
    return rows


def cors_json_response(request: Request, *, status_code: int, content: dict) -> JSONResponse:
    response = JSONResponse(status_code=status_code, content=content)
    origin = request.headers.get("origin", "").strip()
    if origin in ALLOWED_CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"
    return response


app = FastAPI(title="BuildAThon 2026 Workforce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get(REQUEST_ID_HEADER, "").strip() or str(uuid4())
    request.state.request_id = request_id
    started_at = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = int((perf_counter() - started_at) * 1000)
        _record_request_metric(request.method, request.url.path, 500, duration_ms, failed=True)
        logger.exception(
            "request_failed request_id=%s method=%s path=%s duration_ms=%s",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = int((perf_counter() - started_at) * 1000)
    _record_request_metric(request.method, request.url.path, response.status_code, duration_ms, failed=response.status_code >= 500)
    response.headers[REQUEST_ID_HEADER] = request_id
    logger.info(
        "request_complete request_id=%s method=%s path=%s status_code=%s duration_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.middleware("http")
async def authorization_middleware(request: Request, call_next):
    path = request.url.path
    if request.method == "OPTIONS":
        return await call_next(request)
    if any(path.startswith(prefix) for prefix in AUTH_EXEMPT_PATH_PREFIXES):
        return await call_next(request)

    try:
        request.state.auth_principal = resolve_auth_principal(request)
    except HTTPException as exc:
        return cors_json_response(request, status_code=exc.status_code, content={"detail": exc.detail})

    return await call_next(request)


@app.on_event("startup")
def on_startup() -> None:
    bootstrap_application_state()


@app.post("/demo-support/reset")
def reset_demo_support_state(request: Request) -> dict:
    if not demo_reset_enabled():
        raise HTTPException(status_code=404, detail="Not found")

    provided_token = request.headers.get(DEMO_RESET_TOKEN_HEADER, "")
    if provided_token != demo_reset_token():
        raise HTTPException(status_code=403, detail="Invalid demo reset token")

    reset_application_state()
    return {"status": "ok", "mode": "demo-reset"}


@app.post("/test-support/reset")
def reset_test_support_state(request: Request) -> dict:
    if not test_support_enabled():
        raise HTTPException(status_code=404, detail="Not found")

    provided_token = request.headers.get(TEST_SUPPORT_TOKEN_HEADER, "")
    if provided_token != TEST_SUPPORT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid test support token")

    reset_application_state()
    return {"status": "ok"}


@app.get("/health")
def health() -> dict:
    database = get_database_health()
    status = "ok" if database["status"] == "ok" else "degraded"
    return {
        "status": status,
        "timestamp": utc_now_iso(),
        "uptime_seconds": _uptime_seconds(),
        "database": database,
    }


@app.get("/metrics", response_class=PlainTextResponse)
def get_metrics() -> str:
    database = get_database_health()
    runtime = get_database_runtime_info()
    requests_by_path = REQUEST_METRICS.get("requests_by_path", {})
    requests_by_status = REQUEST_METRICS.get("requests_by_status", {})
    lines = [
        "# HELP buildathon_uptime_seconds Application uptime in seconds",
        "# TYPE buildathon_uptime_seconds gauge",
        f"buildathon_uptime_seconds {_uptime_seconds()}",
        "# HELP buildathon_requests_total Total HTTP requests observed by the API",
        "# TYPE buildathon_requests_total counter",
        f"buildathon_requests_total {int(REQUEST_METRICS['request_count_total'])}",
        "# HELP buildathon_request_failures_total Total failed HTTP requests",
        "# TYPE buildathon_request_failures_total counter",
        f"buildathon_request_failures_total {int(REQUEST_METRICS['request_error_count'])}",
        "# HELP buildathon_request_duration_ms_sum Aggregate request duration in milliseconds",
        "# TYPE buildathon_request_duration_ms_sum counter",
        f"buildathon_request_duration_ms_sum {int(REQUEST_METRICS['request_duration_ms_sum'])}",
        "# HELP buildathon_request_duration_ms_max Maximum request duration in milliseconds",
        "# TYPE buildathon_request_duration_ms_max gauge",
        f"buildathon_request_duration_ms_max {int(REQUEST_METRICS['request_duration_ms_max'])}",
        "# HELP buildathon_database_up Database connectivity status",
        "# TYPE buildathon_database_up gauge",
        f"buildathon_database_up {1 if database['status'] == 'ok' else 0}",
        "# HELP buildathon_database_backend_info Database backend metadata",
        "# TYPE buildathon_database_backend_info gauge",
        (
            'buildathon_database_backend_info{backend="%s",driver="%s",database="%s"} 1'
            % (
                _metric_label(runtime["backend"]),
                _metric_label(runtime["driver"]),
                _metric_label(runtime["database"]),
            )
        ),
    ]

    if isinstance(requests_by_path, dict):
        lines.extend(
            (
                'buildathon_requests_by_path_total{route="%s"} %s'
                % (_metric_label(str(route)), int(count))
            )
            for route, count in sorted(requests_by_path.items())
        )
    if isinstance(requests_by_status, dict):
        lines.extend(
            (
                'buildathon_requests_by_status_total{status_code="%s"} %s'
                % (_metric_label(str(status_code)), int(count))
            )
            for status_code, count in sorted(requests_by_status.items())
        )
    return "\n".join(lines) + "\n"


@app.post("/employees/{employee_id}/clock-in")
def clock_in(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)

    open_shift = get_open_shift(db, employee_id)
    if open_shift is not None:
        add_audit_event(db, employee_id, "CLOCK_IN_REJECTED", "Duplicate open shift")
        db.commit()
        raise HTTPException(status_code=409, detail="Duplicate clock-in: open shift exists")

    shift = Shift(
        shift_id=str(uuid4()),
        employee_id=employee_id,
        start_at=utc_now(),
        end_at=None,
        duration_minutes=None,
        state="OPEN",
    )
    db.add(shift)
    add_audit_event(db, employee_id, "CLOCK_IN_ACCEPTED", "Clock-in accepted")
    db.commit()

    return {
        "shift_id": shift.shift_id,
        "employee_id": employee_id,
        "status": "CLOCKED_IN",
        "clock_in_at": shift.start_at.isoformat(),
    }


@app.post("/employees/{employee_id}/clock-out")
def clock_out(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)

    shift = get_open_shift(db, employee_id)
    if shift is None:
        add_audit_event(db, employee_id, "CLOCK_OUT_REJECTED", "No open shift")
        db.commit()
        raise HTTPException(status_code=409, detail="Clock-out rejected: no open shift exists")

    start_at = ensure_utc_datetime(shift.start_at)
    end_dt = utc_now()
    duration_minutes = max(0, int((end_dt - start_at).total_seconds() // 60))

    shift.end_at = end_dt
    shift.duration_minutes = duration_minutes
    shift.state = "CLOSED"
    add_audit_event(db, employee_id, "CLOCK_OUT_ACCEPTED", "Clock-out accepted")
    db.commit()

    return {
        "shift_id": shift.shift_id,
        "employee_id": employee_id,
        "status": "CLOCKED_OUT",
        "clock_out_at": shift.end_at.isoformat() if shift.end_at else None,
        "duration_minutes": duration_minutes,
    }


@app.get("/employees/{employee_id}/shifts")
def get_shifts(employee_id: str, limit: int = 10, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    safe_limit = max(1, min(limit, 100))
    shifts = db.query(Shift).filter(Shift.employee_id == employee_id).order_by(Shift.start_at).all()
    return {"shifts": [shift_to_dict(item) for item in shifts[-safe_limit:]]}


@app.get("/employees/{employee_id}/audit-events")
def get_audit_events(employee_id: str, limit: int = 20, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    safe_limit = max(1, min(limit, 100))
    rows = db.query(AuditEvent).filter(AuditEvent.employee_id == employee_id).order_by(AuditEvent.event_at).all()
    return {"events": [event_to_dict(item) for item in rows[-safe_limit:]]}


@app.get("/employees/{employee_id}/payroll-summary")
def get_payroll_summary(
    employee_id: str,
    period_start: str | None = None,
    period_end: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    ensure_employee_exists(db, employee_id)
    start_date = parse_optional_iso_date(period_start, "period_start")
    end_date = parse_optional_iso_date(period_end, "period_end")
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=422, detail="period_end must be on or after period_start")

    metrics = payroll_metrics(db, employee_id, period_start=start_date, period_end=end_date)
    return {
        "employee_id": employee_id,
        "total_minutes_worked": metrics["total_minutes"],
        "closed_shift_count": metrics["closed_shift_count"],
        "period_start": period_start,
        "period_end": period_end,
    }


@app.get("/employees/{employee_id}/missing-punch-exceptions")
def get_missing_punch_exceptions(employee_id: str, threshold_minutes: int = 60, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    if threshold_minutes <= 0:
        raise HTTPException(status_code=422, detail="threshold_minutes must be greater than 0")

    exceptions: list[dict] = []
    open_shift = get_open_shift(db, employee_id)
    if open_shift is not None:
        start_at = ensure_utc_datetime(open_shift.start_at)
        elapsed_minutes = max(0, int((utc_now() - start_at).total_seconds() // 60))
        if elapsed_minutes >= threshold_minutes:
            exceptions.append(
                {
                    "employee_id": employee_id,
                    "shift_id": open_shift.shift_id,
                    "start_at": start_at.isoformat(),
                    "elapsed_minutes": elapsed_minutes,
                    "status": "MISSING_PUNCH",
                }
            )
    return {"exceptions": exceptions, "threshold_minutes": threshold_minutes}


@app.post("/employees/{employee_id}/time-corrections")
def create_time_correction(employee_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    reason = str(payload.get("reason", "")).strip()
    if not reason:
        raise HTTPException(status_code=422, detail="reason is required")
    if len(reason) > 200:
        raise HTTPException(status_code=422, detail="reason exceeds 200 characters")

    correction = TimeCorrection(
        correction_id=str(uuid4()),
        employee_id=employee_id,
        reason=reason,
        requested_at=utc_now(),
        status="PENDING",
    )
    db.add(correction)
    add_audit_event(db, employee_id, "TIME_CORRECTION_REQUESTED", "Time correction requested")
    db.commit()
    return time_correction_to_dict(correction)


@app.get("/employees/{employee_id}/time-corrections")
def list_time_corrections(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    items = (
        db.query(TimeCorrection)
        .filter(TimeCorrection.employee_id == employee_id)
        .order_by(TimeCorrection.requested_at)
        .all()
    )
    return {"time_corrections": [time_correction_to_dict(item) for item in items]}


@app.post("/employees/{employee_id}/leave-requests")
def create_leave_request(employee_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)

    start_date = str(payload.get("start_date", "")).strip()
    end_date = str(payload.get("end_date", "")).strip()
    if not start_date or not end_date:
        raise HTTPException(status_code=422, detail="start_date and end_date are required")
    start_date_obj = parse_iso_date(start_date, "start_date")
    end_date_obj = parse_iso_date(end_date, "end_date")
    if end_date_obj < start_date_obj:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")

    leave_request = LeaveRequest(
        leave_request_id=str(uuid4()),
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        status="PENDING",
        created_at=utc_now(),
        approved_at=None,
    )
    db.add(leave_request)
    add_audit_event(db, employee_id, "LEAVE_REQUEST_CREATED", "Leave request created")
    db.commit()
    return leave_request_to_dict(leave_request)


@app.get("/employees/{employee_id}/leave-requests")
def list_leave_requests(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    items = db.query(LeaveRequest).filter(LeaveRequest.employee_id == employee_id).order_by(LeaveRequest.created_at).all()
    return {"leave_requests": [leave_request_to_dict(item) for item in items]}


@app.post("/leave-requests/{leave_request_id}/approve")
def approve_leave_request(leave_request_id: str, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "approve_leave")
    leave_request = db.get(LeaveRequest, leave_request_id)
    if leave_request is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if leave_request.status == "APPROVED":
        raise HTTPException(status_code=409, detail="Leave request already approved")
    leave_request.status = "APPROVED"
    leave_request.approved_at = utc_now()
    add_audit_event(db, leave_request.employee_id, "LEAVE_REQUEST_APPROVED", "Leave request approved")
    db.commit()
    return leave_request_to_dict(leave_request)


@app.get("/employees/{employee_id}/leave-balance")
def get_leave_balance(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    used_days = _approved_leave_day_total(db, employee_id)
    total_days = 20
    return {
        "employee_id": employee_id,
        "total_days": total_days,
        "used_days": used_days,
        "remaining_days": max(0, total_days - used_days),
    }


@app.post("/employees/{employee_id}/scheduled-shifts")
def create_scheduled_shift(employee_id: str, payload: dict, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "schedule_shift")
    ensure_employee_exists(db, employee_id)
    policy_config = ensure_policy_settings(db)

    start_at = str(payload.get("start_at", "")).strip()
    end_at = str(payload.get("end_at", "")).strip()
    if not start_at or not end_at:
        raise HTTPException(status_code=422, detail="start_at and end_at are required")
    start_dt = parse_iso_datetime(start_at, "start_at")
    end_dt = parse_iso_datetime(end_at, "end_at")
    if end_dt <= start_dt:
        raise HTTPException(status_code=422, detail="end_at must be after start_at")

    break_minutes = int(payload.get("break_minutes", policy_config["minimum_break_minutes"]))
    if break_minutes < policy_config["minimum_break_minutes"]:
        raise HTTPException(
            status_code=422,
            detail=(
                "break_minutes must be greater than or equal to "
                f"policy minimum {policy_config['minimum_break_minutes']}"
            ),
        )

    break_compliant = True
    covers_core_hours = (
        start_dt.hour <= policy_config["core_hour_start"]
        and end_dt.hour >= policy_config["core_hour_end"]
    )
    if not covers_core_hours:
        raise HTTPException(status_code=422, detail="scheduled shift must cover configured core hours")

    shift = ScheduledShift(
        scheduled_shift_id=str(uuid4()),
        employee_id=employee_id,
        start_at=start_dt,
        end_at=end_dt,
        break_minutes=break_minutes,
        break_compliant=1 if break_compliant else 0,
        covers_core_hours=1 if covers_core_hours else 0,
        status="SCHEDULED",
    )
    db.add(shift)
    add_audit_event(db, employee_id, "SHIFT_SCHEDULED", "Shift scheduled")
    db.commit()
    return scheduled_shift_to_dict(shift)


@app.get("/employees/{employee_id}/scheduled-shifts")
def list_scheduled_shifts(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    items = db.query(ScheduledShift).filter(ScheduledShift.employee_id == employee_id).order_by(ScheduledShift.start_at).all()
    return {"scheduled_shifts": [scheduled_shift_to_dict(item) for item in items]}


@app.get("/employees/{employee_id}/payroll-breakdown")
def get_payroll_breakdown(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    metrics = payroll_metrics(db, employee_id)
    regular_minutes = max(0, metrics["total_minutes"] - metrics["overtime_minutes"])
    return {
        "employee_id": employee_id,
        "total_minutes_worked": metrics["total_minutes"],
        "regular_minutes": regular_minutes,
        "overtime_minutes": metrics["overtime_minutes"],
        "holiday_minutes": metrics["holiday_minutes"],
        "night_shift_minutes": metrics["night_shift_minutes"],
    }


@app.get("/employees/{employee_id}/attendance-exceptions")
def get_attendance_exceptions(employee_id: str, threshold_minutes: int = 60, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    if threshold_minutes <= 0:
        raise HTTPException(status_code=422, detail="threshold_minutes must be greater than 0")

    exceptions: list[dict] = []
    missing = get_missing_punch_exceptions(employee_id, threshold_minutes=threshold_minutes, db=db)["exceptions"]
    for item in missing:
        exceptions.append(
            {
                "type": "MISSING_PUNCH",
                "employee_id": employee_id,
                "reference_id": item["shift_id"],
                "details": f"Open shift for {item['elapsed_minutes']} minutes",
            }
        )

    scheduled = db.query(ScheduledShift).filter(ScheduledShift.employee_id == employee_id).all()
    for shift in scheduled:
        if not bool(shift.break_compliant):
            exceptions.append(
                {
                    "type": "BREAK_POLICY_VIOLATION",
                    "employee_id": employee_id,
                    "reference_id": shift.scheduled_shift_id,
                    "details": "Break minutes below policy minimum",
                }
            )
        if not bool(shift.covers_core_hours):
            exceptions.append(
                {
                    "type": "CORE_HOUR_VIOLATION",
                    "employee_id": employee_id,
                    "reference_id": shift.scheduled_shift_id,
                    "details": "Scheduled shift does not cover configured core hours",
                }
            )

    return {"employee_id": employee_id, "exceptions": exceptions}


@app.get("/employees/{employee_id}/compliance-report")
def get_compliance_report(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    return _build_compliance_report(db, employee_id)


@app.get("/employees/{employee_id}/timesheets")
def get_timesheet(
    employee_id: str,
    period_start: str | None = None,
    period_end: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    ensure_employee_exists(db, employee_id)
    start_date = parse_optional_iso_date(period_start, "period_start")
    end_date = parse_optional_iso_date(period_end, "period_end")
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=422, detail="period_end must be on or after period_start")

    entries: list[dict] = []
    for shift in _get_closed_shift_query(db, employee_id).all():
        shift_date = shift.start_at.date()
        if start_date and shift_date < start_date:
            continue
        if end_date and shift_date > end_date:
            continue
        entries.append(
            {
                "shift_id": shift.shift_id,
                "date": shift_date.isoformat(),
                "minutes": int(shift.duration_minutes or 0),
                "start_at": shift.start_at.isoformat(),
                "end_at": shift.end_at.isoformat() if shift.end_at else None,
            }
        )

    return {
        "employee_id": employee_id,
        "period_start": period_start,
        "period_end": period_end,
        "entries": entries,
        "total_minutes": sum(item["minutes"] for item in entries),
    }


@app.get("/employees/{employee_id}/pto-balance")
def get_pto_balance(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    pto_adjustments = db.query(PtoAdjustment).filter(PtoAdjustment.employee_id == employee_id).all()
    total_days = 20 + sum(item.days_delta for item in pto_adjustments)
    used_days = _approved_leave_day_total(db, employee_id)
    return {
        "employee_id": employee_id,
        "total_days": total_days,
        "used_days": used_days,
        "remaining_days": max(0, total_days - used_days),
    }


@app.post("/employees/{employee_id}/pto-adjustments")
def adjust_pto_balance(employee_id: str, payload: dict, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "adjust_balances")
    ensure_employee_exists(db, employee_id)
    days_delta = int(payload.get("days_delta", 0))
    if days_delta == 0:
        raise HTTPException(status_code=422, detail="days_delta cannot be 0")

    adjustment = PtoAdjustment(
        adjustment_id=str(uuid4()),
        employee_id=employee_id,
        days_delta=days_delta,
        created_at=utc_now(),
    )
    db.add(adjustment)
    add_audit_event(db, employee_id, "PTO_ADJUSTED", f"PTO adjusted by {days_delta} day(s)")
    db.commit()
    total_adjustment = sum(
        item.days_delta for item in db.query(PtoAdjustment).filter(PtoAdjustment.employee_id == employee_id).all()
    )
    return {
        "adjustment_id": adjustment.adjustment_id,
        "employee_id": employee_id,
        "days_delta": days_delta,
        "created_at": adjustment.created_at.isoformat(),
        "total_adjustment": total_adjustment,
    }


@app.get("/employees/{employee_id}/comp-time-balance")
def get_comp_time_balance(employee_id: str, db: Session = Depends(get_db)) -> dict:
    ensure_employee_exists(db, employee_id)
    accrued_from_overtime = payroll_metrics(db, employee_id)["overtime_minutes"]
    manual_adjustment = sum(
        item.minutes_delta
        for item in db.query(CompTimeAdjustment).filter(CompTimeAdjustment.employee_id == employee_id).all()
    )
    total_minutes = max(0, accrued_from_overtime + manual_adjustment)
    return {
        "employee_id": employee_id,
        "accrued_from_overtime_minutes": accrued_from_overtime,
        "manual_adjustment_minutes": manual_adjustment,
        "total_comp_time_minutes": total_minutes,
    }


@app.post("/employees/{employee_id}/comp-time-adjustments")
def adjust_comp_time_balance(employee_id: str, payload: dict, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "adjust_balances")
    ensure_employee_exists(db, employee_id)
    minutes_delta = int(payload.get("minutes_delta", 0))
    reason = str(payload.get("reason", "")).strip()
    if minutes_delta == 0:
        raise HTTPException(status_code=422, detail="minutes_delta cannot be 0")
    if not reason:
        raise HTTPException(status_code=422, detail="reason is required")

    adjustment = CompTimeAdjustment(
        adjustment_id=str(uuid4()),
        employee_id=employee_id,
        minutes_delta=minutes_delta,
        reason=reason,
        created_at=utc_now(),
    )
    db.add(adjustment)
    add_audit_event(db, employee_id, "COMP_TIME_ADJUSTED", f"Comp-time adjusted by {minutes_delta} minute(s)")
    db.commit()
    return comp_time_adjustment_to_dict(adjustment)


@app.get("/companies/{company_id}/employees")
def list_company_employees(company_id: str, db: Session = Depends(get_db)) -> dict:
    employees = db.query(Employee).filter(Employee.company_id == company_id).order_by(Employee.employee_id).all()
    return {
        "employees": [
            {"employee_id": item.employee_id, "company_id": item.company_id, "location_id": item.location_id}
            for item in employees
        ]
    }


@app.patch("/companies/{company_id}/employees/{employee_id}")
def update_company_employee(company_id: str, employee_id: str, payload: dict, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "policy_configure")
    require_company_access(request, company_id)
    employee = db.get(Employee, employee_id)
    if employee is None or employee.company_id != company_id:
        raise HTTPException(status_code=404, detail="Employee not found for company")

    location_id = str(payload.get("location_id", "")).strip().upper()
    if not location_id:
        raise HTTPException(status_code=422, detail="location_id is required")
    if len(location_id) > 64:
        raise HTTPException(status_code=422, detail="location_id exceeds 64 characters")

    employee.location_id = location_id
    add_audit_event(db, employee.employee_id, "EMPLOYEE_LOCATION_UPDATED", f"Employee moved to {location_id}")
    db.commit()
    return {"employee_id": employee.employee_id, "company_id": employee.company_id, "location_id": employee.location_id}


@app.get("/companies/{company_id}/locations")
def list_company_locations(company_id: str, db: Session = Depends(get_db)) -> dict:
    employees = db.query(Employee).filter(Employee.company_id == company_id).all()
    location_counts: dict[str, int] = {}
    for employee in employees:
        location_counts[employee.location_id] = location_counts.get(employee.location_id, 0) + 1

    locations = [
        {"location_id": location_id, "employee_count": count}
        for location_id, count in sorted(location_counts.items())
    ]
    return {"company_id": company_id, "locations": locations}


@app.get("/companies/{company_id}/locations/{location_id}/employees")
def list_location_employees(company_id: str, location_id: str, db: Session = Depends(get_db)) -> dict:
    employees = (
        db.query(Employee)
        .filter(Employee.company_id == company_id, Employee.location_id == location_id)
        .order_by(Employee.employee_id)
        .all()
    )
    if not employees:
        raise HTTPException(status_code=404, detail="Location not found for company")

    return {
        "company_id": company_id,
        "location_id": location_id,
        "employees": [
            {"employee_id": item.employee_id, "company_id": item.company_id, "location_id": item.location_id}
            for item in employees
        ],
    }


@app.get("/companies/{company_id}/notification-settings")
def get_notification_settings(company_id: str, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "policy_configure")
    require_company_access(request, company_id)
    return _notification_endpoint_to_dict(db.get(NotificationEndpoint, company_id), company_id)


@app.put("/companies/{company_id}/notification-settings")
def save_notification_settings(company_id: str, payload: dict, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "policy_configure")
    require_company_access(request, company_id)

    destination_type = str(payload.get("destination_type", "WEBHOOK")).strip().upper()
    target = str(payload.get("target", "")).strip()
    secret_reference = str(payload.get("secret_reference", "")).strip() or None
    enabled = bool(payload.get("enabled", False))

    if destination_type not in ALLOWED_NOTIFICATION_DESTINATIONS:
        raise HTTPException(status_code=422, detail="destination_type is not supported")
    if enabled and not target:
        raise HTTPException(status_code=422, detail="target is required when notifications are enabled")

    item = db.get(NotificationEndpoint, company_id)
    if item is None:
        item = NotificationEndpoint(
            company_id=company_id,
            destination_type=destination_type,
            target=target,
            secret_reference=secret_reference,
            enabled=1 if enabled else 0,
            status="CONFIGURED" if enabled else "DISABLED",
            last_tested_at=None,
        )
        db.add(item)
    else:
        item.destination_type = destination_type
        item.target = target
        item.secret_reference = secret_reference
        item.enabled = 1 if enabled else 0
        item.status = "CONFIGURED" if enabled else "DISABLED"

    db.commit()
    return _notification_endpoint_to_dict(item, company_id)


@app.post("/companies/{company_id}/notification-settings/test")
def test_notification_settings(company_id: str, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "policy_configure")
    require_company_access(request, company_id)
    item = db.get(NotificationEndpoint, company_id)
    if item is None or not bool(item.enabled) or not item.target:
        raise HTTPException(status_code=409, detail="Notification stub is not configured")

    item.last_tested_at = utc_now()
    item.status = "TEST_DELIVERY_SIMULATED"
    db.commit()
    return {
        "company_id": company_id,
        "destination_type": item.destination_type,
        "target": item.target,
        "status": item.status,
        "tested_at": item.last_tested_at.isoformat() if item.last_tested_at else None,
        "delivery_mode": "STUB",
    }


@app.get("/companies/{company_id}/secret-provider")
def get_secret_provider(company_id: str, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "policy_configure")
    require_company_access(request, company_id)
    return _secret_provider_to_dict(db.get(SecretProviderConfig, company_id), company_id)


@app.put("/companies/{company_id}/secret-provider")
def save_secret_provider(company_id: str, payload: dict, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "policy_configure")
    require_company_access(request, company_id)

    provider = str(payload.get("provider", "ENV")).strip().upper()
    reference_name = str(payload.get("reference_name", "")).strip()
    enabled = bool(payload.get("enabled", False))

    if provider not in ALLOWED_SECRET_PROVIDERS:
        raise HTTPException(status_code=422, detail="provider is not supported")
    if enabled and not reference_name:
        raise HTTPException(status_code=422, detail="reference_name is required when secret support is enabled")

    item = db.get(SecretProviderConfig, company_id)
    if item is None:
        item = SecretProviderConfig(
            company_id=company_id,
            provider=provider,
            reference_name=reference_name,
            enabled=1 if enabled else 0,
            status="CONFIGURED" if enabled else "DISABLED",
            updated_at=utc_now(),
        )
        db.add(item)
    else:
        item.provider = provider
        item.reference_name = reference_name
        item.enabled = 1 if enabled else 0
        item.status = "CONFIGURED" if enabled else "DISABLED"
        item.updated_at = utc_now()

    db.commit()
    return _secret_provider_to_dict(item, company_id)


@app.get("/companies/{company_id}/payroll-export")
def get_payroll_export(
    company_id: str,
    request: Request,
    period_start: str | None = None,
    period_end: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    require_action(request, "payroll_export")
    require_company_access(request, company_id)
    start_date = parse_optional_iso_date(period_start, "period_start")
    end_date = parse_optional_iso_date(period_end, "period_end")
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=422, detail="period_end must be on or after period_start")
    if period_start:
        parse_iso_date(period_start, "period_start")
    if period_end:
        parse_iso_date(period_end, "period_end")

    rows = _build_company_payroll_rows(db, company_id, period_start=start_date, period_end=end_date)
    return {
        "export_id": str(uuid4()),
        "company_id": company_id,
        "generated_at": utc_now_iso(),
        "period_start": period_start,
        "period_end": period_end,
        "row_count": len(rows),
        "status": "READY",
        "rows": rows,
    }


@app.get("/companies/{company_id}/locations/{location_id}/payroll-export")
def get_location_payroll_export(
    company_id: str,
    location_id: str,
    request: Request,
    period_start: str | None = None,
    period_end: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    require_action(request, "payroll_export")
    require_company_access(request, company_id)
    start_date = parse_optional_iso_date(period_start, "period_start")
    end_date = parse_optional_iso_date(period_end, "period_end")
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=422, detail="period_end must be on or after period_start")
    if period_start:
        parse_iso_date(period_start, "period_start")
    if period_end:
        parse_iso_date(period_end, "period_end")

    rows = _build_location_payroll_rows(
        db,
        company_id,
        location_id,
        period_start=start_date,
        period_end=end_date,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Location not found for company")

    return {
        "export_id": str(uuid4()),
        "company_id": company_id,
        "location_id": location_id,
        "generated_at": utc_now_iso(),
        "period_start": period_start,
        "period_end": period_end,
        "row_count": len(rows),
        "status": "READY",
        "rows": rows,
    }


@app.get("/companies/{company_id}/payroll-integration-payload")
def get_payroll_integration_payload(company_id: str, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "payroll_integration")
    require_company_access(request, company_id)
    rows = _build_company_payroll_rows(db, company_id)
    return {
        "company_id": company_id,
        "generated_at": utc_now_iso(),
        "schema_version": "1.0",
        "destination": "future-payroll-integration",
        "employees": rows,
    }


@app.get("/reports/operational")
def get_operational_report(request: Request, company_id: str | None = None, db: Session = Depends(get_db)) -> dict:
    require_action(request, "view_reports")
    if company_id is not None:
        require_company_access(request, company_id)
    employees_q = db.query(Employee)
    if company_id is not None:
        employees_q = employees_q.filter(Employee.company_id == company_id)
    employees = employees_q.all()
    employee_ids = {item.employee_id for item in employees}

    events = db.query(AuditEvent).filter(AuditEvent.employee_id.in_(employee_ids)).all() if employee_ids else []
    rejections = [event for event in events if event.event_type.endswith("REJECTED")]
    accepts = [event for event in events if event.event_type.endswith("ACCEPTED")]

    open_shift_count = db.query(Shift).filter(Shift.employee_id.in_(employee_ids), Shift.state == "OPEN").count() if employee_ids else 0
    closed_shift_count = db.query(Shift).filter(Shift.employee_id.in_(employee_ids), Shift.state == "CLOSED").count() if employee_ids else 0

    return {
        "company_id": company_id,
        "event_count": len(events),
        "accepted_event_count": len(accepts),
        "rejected_event_count": len(rejections),
        "open_shift_count": open_shift_count,
        "closed_shift_count": closed_shift_count,
    }


@app.get("/reports/crosscheck")
def get_crosscheck_report(employee_id: str, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "view_reports")
    ensure_employee_exists(db, employee_id)
    summary = get_payroll_summary(employee_id, db=db)
    derived_total = sum(int(item.duration_minutes or 0) for item in list_closed_shifts(db, employee_id))
    return {
        "employee_id": employee_id,
        "payroll_summary_total_minutes": summary["total_minutes_worked"],
        "derived_shift_total_minutes": derived_total,
        "status": "MATCH" if summary["total_minutes_worked"] == derived_total else "MISMATCH",
    }


@app.get("/policies")
def get_policy_config(db: Session = Depends(get_db)) -> dict:
    return {"policies": ensure_policy_settings(db)}


@app.patch("/policies")
def update_policy_config(payload: dict, request: Request, db: Session = Depends(get_db)) -> dict:
    require_action(request, "policy_configure")
    current = ensure_policy_settings(db)
    min_break = payload.get("minimum_break_minutes")
    core_start = payload.get("core_hour_start")
    core_end = payload.get("core_hour_end")
    updated = dict(current)

    if min_break is not None:
        min_break_int = int(min_break)
        if min_break_int <= 0:
            raise HTTPException(status_code=422, detail="minimum_break_minutes must be greater than 0")
        updated["minimum_break_minutes"] = min_break_int

    if core_start is not None:
        core_start_int = int(core_start)
        if core_start_int < 0 or core_start_int > 23:
            raise HTTPException(status_code=422, detail="core_hour_start must be between 0 and 23")
        updated["core_hour_start"] = core_start_int

    if core_end is not None:
        core_end_int = int(core_end)
        if core_end_int < 1 or core_end_int > 24:
            raise HTTPException(status_code=422, detail="core_hour_end must be between 1 and 24")
        updated["core_hour_end"] = core_end_int

    if updated["core_hour_start"] >= updated["core_hour_end"]:
        raise HTTPException(status_code=422, detail="core_hour_start must be earlier than core_hour_end")

    return {"policies": save_policy_values(db, updated)}


@app.post("/authz/check")
def check_authorization(payload: dict) -> dict:
    role = str(payload.get("role", "")).strip().upper()
    action = str(payload.get("action", "")).strip()
    if not role or not action:
        raise HTTPException(status_code=422, detail="role and action are required")
    allowed = action in ROLE_PERMISSIONS.get(role, set())
    return {"role": role, "action": action, "allowed": allowed}


@app.get("/ops/diagnostics")
def get_ops_diagnostics(db: Session = Depends(get_db)) -> dict:
    database = get_database_health()
    policy_config = ensure_policy_settings(db)
    return {
        "open_shift_count": db.query(Shift).filter(Shift.state == "OPEN").count(),
        "shift_count": db.query(Shift).count(),
        "audit_event_count": db.query(AuditEvent).count(),
        "leave_request_count": db.query(LeaveRequest).count(),
        "scheduled_shift_count": db.query(ScheduledShift).count(),
        "time_correction_count": db.query(TimeCorrection).count(),
        "pto_adjustment_count": db.query(PtoAdjustment).count(),
        "comp_time_adjustment_count": db.query(CompTimeAdjustment).count(),
        "policy_count": len(policy_config),
        "uptime_seconds": _uptime_seconds(),
        "request_count_total": int(REQUEST_METRICS["request_count_total"]),
        "request_error_count": int(REQUEST_METRICS["request_error_count"]),
        "request_duration_ms_max": int(REQUEST_METRICS["request_duration_ms_max"]),
        "database_backend": database["backend"],
        "database_status": database["status"],
    }
