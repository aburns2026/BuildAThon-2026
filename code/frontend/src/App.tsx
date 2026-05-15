import { useEffect, useMemo, useState } from "react";

type Shift = {
  shift_id: string;
  employee_id: string;
  start_at: string;
  end_at: string | null;
  duration_minutes: number | null;
  state: "OPEN" | "CLOSED";
};

type AuditEvent = {
  event_id: string;
  employee_id: string;
  event_type: string;
  event_at: string;
  details: string;
};

type PayrollSummary = {
  employee_id: string;
  total_minutes_worked: number;
  closed_shift_count: number;
  period_start: string | null;
  period_end: string | null;
};

type PayrollBreakdown = {
  employee_id: string;
  total_minutes_worked: number;
  regular_minutes: number;
  overtime_minutes: number;
  holiday_minutes: number;
  night_shift_minutes: number;
};

type MissingPunchException = {
  employee_id: string;
  shift_id: string;
  start_at: string;
  elapsed_minutes: number;
  status: "MISSING_PUNCH";
};

type LeaveRequest = {
  leave_request_id: string;
  employee_id: string;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
  approved_at: string | null;
};

type LeaveBalance = {
  employee_id: string;
  total_days: number;
  used_days: number;
  remaining_days: number;
};

type PtoBalance = {
  employee_id: string;
  total_days: number;
  used_days: number;
  remaining_days: number;
};

type CompTimeBalance = {
  employee_id: string;
  accrued_from_overtime_minutes: number;
  manual_adjustment_minutes: number;
  total_comp_time_minutes: number;
};

type ScheduledShift = {
  scheduled_shift_id: string;
  employee_id: string;
  start_at: string;
  end_at: string;
  break_minutes: number;
  break_compliant: boolean;
  covers_core_hours: boolean;
  status: string;
};

type PolicyConfig = {
  minimum_break_minutes: number;
  core_hour_start: number;
  core_hour_end: number;
};

type CompanyEmployee = {
  employee_id: string;
  company_id: string;
  location_id: string;
};

type CompanyLocation = {
  location_id: string;
  employee_count: number;
};

type OperationalReport = {
  company_id: string | null;
  event_count: number;
  accepted_event_count: number;
  rejected_event_count: number;
  open_shift_count: number;
  closed_shift_count: number;
};

type CrosscheckReport = {
  employee_id: string;
  payroll_summary_total_minutes: number;
  derived_shift_total_minutes: number;
  status: "MATCH" | "MISMATCH";
};

type PayrollExportSummary = {
  company_id: string;
  location_id?: string;
  generated_at: string;
  row_count: number;
  status: string;
};

type PayrollIntegrationRow = {
  employee_id: string;
  location_id: string;
  total_minutes_worked: number;
  overtime_minutes: number;
  holiday_minutes: number;
  night_shift_minutes: number;
};

type PayrollIntegrationPayload = {
  company_id: string;
  generated_at: string;
  schema_version: string;
  destination: string;
  employees: PayrollIntegrationRow[];
};

type NotificationSettings = {
  company_id: string;
  destination_type: string;
  target: string;
  secret_reference: string | null;
  enabled: boolean;
  status: string;
  last_tested_at: string | null;
  delivery_mode: string;
};

type SecretProviderSettings = {
  company_id: string;
  provider: string;
  reference_name: string;
  enabled: boolean;
  status: string;
  stores_secret_material: boolean;
  updated_at: string | null;
};

type ComplianceValidation = {
  rule: string;
  status: "PASS" | "WARN" | "FAIL";
  details: string;
};

type ComplianceReport = {
  employee_id: string;
  tax_validation_status: "PASS" | "WARN" | "FAIL";
  labor_rule_validation_status: "PASS" | "WARN" | "FAIL";
  attendance_exception_count: number;
  tax_validations: ComplianceValidation[];
  labor_rule_validations: ComplianceValidation[];
};

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://127.0.0.1:8000";
const DEFAULT_API_BEARER_TOKEN =
  (import.meta.env.VITE_DEMO_AUTH_TOKEN as string | undefined) ?? "demo-employee-token";
const DEFAULT_API_MANAGER_TOKEN =
  (import.meta.env.VITE_MANAGER_AUTH_TOKEN as string | undefined) ?? "demo-manager-token";
const DEFAULT_API_PAYROLL_TOKEN =
  (import.meta.env.VITE_PAYROLL_AUTH_TOKEN as string | undefined) ?? "demo-payroll-token";
const DEFAULT_API_ADMIN_TOKEN =
  (import.meta.env.VITE_ADMIN_AUTH_TOKEN as string | undefined) ?? "demo-admin-token";

const TOKEN_OVERRIDE_STORAGE_KEYS = {
  employee: "buildathon.demoAuthToken",
  manager: "buildathon.managerAuthToken",
  payroll: "buildathon.payrollAuthToken",
  admin: "buildathon.adminAuthToken",
} as const;

const DEMO_EMPLOYEE_ID = "E001";
const DEMO_COMPANY_ID = "COMP-001";
const ADMIN_HEADERS = { "x-role": "ADMIN", "x-company-id": DEMO_COMPANY_ID };

function readRuntimeOverride(storageKey: string): string | undefined {
  if (typeof window === "undefined") {
    return undefined;
  }
  try {
    const value = window.localStorage.getItem(storageKey)?.trim();
    return value ? value : undefined;
  } catch {
    return undefined;
  }
}

function getEmployeeToken(): string {
  return readRuntimeOverride(TOKEN_OVERRIDE_STORAGE_KEYS.employee) ?? DEFAULT_API_BEARER_TOKEN;
}

function getManagerToken(): string {
  return readRuntimeOverride(TOKEN_OVERRIDE_STORAGE_KEYS.manager) ?? DEFAULT_API_MANAGER_TOKEN;
}

function getPayrollToken(): string {
  return readRuntimeOverride(TOKEN_OVERRIDE_STORAGE_KEYS.payroll) ?? DEFAULT_API_PAYROLL_TOKEN;
}

function getAdminToken(): string {
  return readRuntimeOverride(TOKEN_OVERRIDE_STORAGE_KEYS.admin) ?? DEFAULT_API_ADMIN_TOKEN;
}

function formatDate(value: string | null): string {
  if (!value) {
    return "-";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString();
}

function formatMinutes(value: number): string {
  return `${value} min`;
}

function formatRuleLabel(value: string): string {
  return value.replace(/_/g, " ");
}

function getStatusClassName(value: string): string {
  return `status-pill ${value.toLowerCase()}`;
}

export default function App() {
  const [message, setMessage] = useState("Ready");
  const [status, setStatus] = useState<"CLOCKED_IN" | "CLOCKED_OUT" | "UNKNOWN">("UNKNOWN");
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [summary, setSummary] = useState<PayrollSummary | null>(null);
  const [payrollBreakdown, setPayrollBreakdown] = useState<PayrollBreakdown | null>(null);
  const [complianceReport, setComplianceReport] = useState<ComplianceReport | null>(null);
  const [exceptions, setExceptions] = useState<MissingPunchException[]>([]);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [leaveBalance, setLeaveBalance] = useState<LeaveBalance | null>(null);
  const [ptoBalance, setPtoBalance] = useState<PtoBalance | null>(null);
  const [compTimeBalance, setCompTimeBalance] = useState<CompTimeBalance | null>(null);
  const [scheduledShifts, setScheduledShifts] = useState<ScheduledShift[]>([]);
  const [policyConfig, setPolicyConfig] = useState<PolicyConfig | null>(null);
  const [companyEmployees, setCompanyEmployees] = useState<CompanyEmployee[]>([]);
  const [companyLocations, setCompanyLocations] = useState<CompanyLocation[]>([]);
  const [operationalReport, setOperationalReport] = useState<OperationalReport | null>(null);
  const [crosscheckReport, setCrosscheckReport] = useState<CrosscheckReport | null>(null);
  const [payrollExport, setPayrollExport] = useState<PayrollExportSummary | null>(null);
  const [locationPayrollExport, setLocationPayrollExport] = useState<PayrollExportSummary | null>(null);
  const [payrollIntegrationPayload, setPayrollIntegrationPayload] = useState<PayrollIntegrationPayload | null>(null);
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings | null>(null);
  const [secretProvider, setSecretProvider] = useState<SecretProviderSettings | null>(null);
  const [leaveStartDate, setLeaveStartDate] = useState("2026-05-20");
  const [leaveEndDate, setLeaveEndDate] = useState("2026-05-21");
  const [ptoAdjustmentDays, setPtoAdjustmentDays] = useState("2");
  const [compTimeAdjustmentMinutes, setCompTimeAdjustmentMinutes] = useState("30");
  const [compTimeAdjustmentReason, setCompTimeAdjustmentReason] = useState("Manual correction");
  const [scheduledStartAt, setScheduledStartAt] = useState("2026-05-22T09:00");
  const [scheduledEndAt, setScheduledEndAt] = useState("2026-05-22T17:00");
  const [scheduledBreakMinutes, setScheduledBreakMinutes] = useState("30");
  const [policyDraft, setPolicyDraft] = useState({
    minimum_break_minutes: "30",
    core_hour_start: "10",
    core_hour_end: "15",
  });
  const [selectedPayrollLocationId, setSelectedPayrollLocationId] = useState("LOC-001");
  const [selectedAdminEmployeeId, setSelectedAdminEmployeeId] = useState(DEMO_EMPLOYEE_ID);
  const [adminLocationId, setAdminLocationId] = useState("LOC-001");
  const [notificationDraft, setNotificationDraft] = useState({
    destination_type: "WEBHOOK",
    target: "",
    secret_reference: "",
    enabled: false,
  });
  const [secretDraft, setSecretDraft] = useState({
    provider: "ENV",
    reference_name: "",
    enabled: false,
  });
  const [busy, setBusy] = useState(false);

  const headerSub = useMemo(
    () =>
      status === "UNKNOWN"
        ? "No recent action"
        : status === "CLOCKED_IN"
          ? "Employee currently clocked in"
          : "Employee currently clocked out",
    [status]
  );

  async function apiRequest(
    path: string,
    init?: RequestInit,
    options?: { token?: string; extraHeaders?: Record<string, string> }
  ): Promise<Response> {
    return fetch(`${API_BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${options?.token ?? getEmployeeToken()}`,
        ...(options?.extraHeaders ?? {}),
      },
      ...init,
    });
  }

  async function refreshReadModels() {
    const [
      shiftRes,
      auditRes,
      summaryRes,
      breakdownRes,
      complianceRes,
      exceptionRes,
      leaveRequestRes,
      leaveBalanceRes,
      ptoBalanceRes,
      compTimeBalanceRes,
      scheduledShiftRes,
      policiesRes,
      companyEmployeesRes,
      companyLocationsRes,
      operationalReportRes,
      crosscheckReportRes,
      payrollExportRes,
      payrollIntegrationPayloadRes,
      notificationSettingsRes,
      secretProviderRes,
    ] = await Promise.all([
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/shifts`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/audit-events`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/payroll-summary`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/payroll-breakdown`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/compliance-report`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/missing-punch-exceptions?threshold_minutes=60`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/leave-requests`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/leave-balance`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/pto-balance`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/comp-time-balance`),
      apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/scheduled-shifts`),
      apiRequest(`/policies`),
      apiRequest(`/companies/${DEMO_COMPANY_ID}/employees`, undefined, {
        token: getAdminToken(),
        extraHeaders: ADMIN_HEADERS,
      }),
      apiRequest(`/companies/${DEMO_COMPANY_ID}/locations`, undefined, {
        token: getAdminToken(),
        extraHeaders: ADMIN_HEADERS,
      }),
      apiRequest(`/reports/operational?company_id=${DEMO_COMPANY_ID}`, undefined, {
        token: getManagerToken(),
        extraHeaders: { "x-role": "MANAGER", "x-company-id": DEMO_COMPANY_ID },
      }),
      apiRequest(`/reports/crosscheck?employee_id=${DEMO_EMPLOYEE_ID}`, undefined, {
        token: getManagerToken(),
        extraHeaders: { "x-role": "MANAGER" },
      }),
      apiRequest(`/companies/${DEMO_COMPANY_ID}/payroll-export`, undefined, {
        token: getPayrollToken(),
        extraHeaders: { "x-role": "PAYROLL", "x-company-id": DEMO_COMPANY_ID },
      }),
      apiRequest(`/companies/${DEMO_COMPANY_ID}/payroll-integration-payload`, undefined, {
        token: getPayrollToken(),
        extraHeaders: { "x-role": "PAYROLL", "x-company-id": DEMO_COMPANY_ID },
      }),
      apiRequest(`/companies/${DEMO_COMPANY_ID}/notification-settings`, undefined, {
        token: getAdminToken(),
        extraHeaders: ADMIN_HEADERS,
      }),
      apiRequest(`/companies/${DEMO_COMPANY_ID}/secret-provider`, undefined, {
        token: getAdminToken(),
        extraHeaders: ADMIN_HEADERS,
      }),
    ]);

    if (shiftRes.ok) {
      const shiftBody = await shiftRes.json();
      setShifts(shiftBody.shifts ?? []);
    }

    if (auditRes.ok) {
      const auditBody = await auditRes.json();
      setEvents(auditBody.events ?? []);
    }

    if (summaryRes.ok) {
      const summaryBody = await summaryRes.json();
      setSummary(summaryBody);
    }

    if (breakdownRes.ok) {
      const breakdownBody = await breakdownRes.json();
      setPayrollBreakdown(breakdownBody);
    }

    if (complianceRes.ok) {
      const complianceBody = await complianceRes.json();
      setComplianceReport(complianceBody);
    }

    if (exceptionRes.ok) {
      const exceptionBody = await exceptionRes.json();
      setExceptions(exceptionBody.exceptions ?? []);
    }

    if (leaveRequestRes.ok) {
      const leaveRequestBody = await leaveRequestRes.json();
      setLeaveRequests(leaveRequestBody.leave_requests ?? []);
    }

    if (leaveBalanceRes.ok) {
      const leaveBalanceBody = await leaveBalanceRes.json();
      setLeaveBalance(leaveBalanceBody);
    }

    if (ptoBalanceRes.ok) {
      const ptoBalanceBody = await ptoBalanceRes.json();
      setPtoBalance(ptoBalanceBody);
    }

    if (compTimeBalanceRes.ok) {
      const compTimeBalanceBody = await compTimeBalanceRes.json();
      setCompTimeBalance(compTimeBalanceBody);
    }

    if (scheduledShiftRes.ok) {
      const scheduledShiftBody = await scheduledShiftRes.json();
      setScheduledShifts(scheduledShiftBody.scheduled_shifts ?? []);
    }

    if (policiesRes.ok) {
      const policiesBody = await policiesRes.json();
      setPolicyConfig(policiesBody.policies ?? null);
    }

    if (companyEmployeesRes.ok) {
      const companyEmployeesBody = await companyEmployeesRes.json();
      setCompanyEmployees(companyEmployeesBody.employees ?? []);
    }

    if (companyLocationsRes.ok) {
      const companyLocationsBody = await companyLocationsRes.json();
      const nextLocations = companyLocationsBody.locations ?? [];
      setCompanyLocations(nextLocations);

      const selectedLocationStillExists = nextLocations.some(
        (location: CompanyLocation) => location.location_id === selectedPayrollLocationId
      );
      const nextLocationId = selectedLocationStillExists
        ? selectedPayrollLocationId
        : (nextLocations[0]?.location_id ?? "");

      if (nextLocationId && nextLocationId !== selectedPayrollLocationId) {
        setSelectedPayrollLocationId(nextLocationId);
      }

      if (nextLocationId) {
        await refreshLocationPayrollExport(nextLocationId);
      } else {
        setLocationPayrollExport(null);
      }
    }

    if (operationalReportRes.ok) {
      const operationalReportBody = await operationalReportRes.json();
      setOperationalReport(operationalReportBody);
    }

    if (crosscheckReportRes.ok) {
      const crosscheckReportBody = await crosscheckReportRes.json();
      setCrosscheckReport(crosscheckReportBody);
    }

    if (payrollExportRes.ok) {
      const payrollExportBody = await payrollExportRes.json();
      setPayrollExport(payrollExportBody);
    }

    if (payrollIntegrationPayloadRes.ok) {
      const payrollIntegrationPayloadBody = await payrollIntegrationPayloadRes.json();
      setPayrollIntegrationPayload(payrollIntegrationPayloadBody);
    }

    if (notificationSettingsRes.ok) {
      const notificationBody = await notificationSettingsRes.json();
      setNotificationSettings({
        company_id: notificationBody.company_id ?? DEMO_COMPANY_ID,
        destination_type: notificationBody.destination_type ?? "WEBHOOK",
        target: notificationBody.target ?? "",
        secret_reference: notificationBody.secret_reference ?? null,
        enabled: Boolean(notificationBody.enabled),
        status: notificationBody.status ?? "NOT_CONFIGURED",
        last_tested_at: notificationBody.last_tested_at ?? null,
        delivery_mode: notificationBody.delivery_mode ?? "STUB",
      });
    }

    if (secretProviderRes.ok) {
      const secretBody = await secretProviderRes.json();
      setSecretProvider({
        company_id: secretBody.company_id ?? DEMO_COMPANY_ID,
        provider: secretBody.provider ?? "ENV",
        reference_name: secretBody.reference_name ?? "",
        enabled: Boolean(secretBody.enabled),
        status: secretBody.status ?? "NOT_CONFIGURED",
        stores_secret_material: Boolean(secretBody.stores_secret_material),
        updated_at: secretBody.updated_at ?? null,
      });
    }
  }

  async function refreshLocationPayrollExport(locationId: string) {
    const response = await apiRequest(
      `/companies/${DEMO_COMPANY_ID}/locations/${locationId}/payroll-export`,
      undefined,
      {
        token: getPayrollToken(),
        extraHeaders: { "x-role": "PAYROLL", "x-company-id": DEMO_COMPANY_ID },
      }
    );

    if (!response.ok) {
      setLocationPayrollExport(null);
      return;
    }

    const body = await response.json();
    setLocationPayrollExport(body);
  }

  async function runPunch(action: "in" | "out") {
    setBusy(true);
    const endpoint =
      action === "in"
        ? `/employees/${DEMO_EMPLOYEE_ID}/clock-in`
        : `/employees/${DEMO_EMPLOYEE_ID}/clock-out`;

    try {
      const response = await apiRequest(endpoint, { method: "POST" });
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Request failed");
      } else {
        const newStatus = body.status as "CLOCKED_IN" | "CLOCKED_OUT";
        setStatus(newStatus);
        setMessage(
          action === "in"
            ? `Clock-in accepted at ${formatDate(body.clock_in_at)}`
            : `Clock-out accepted at ${formatDate(body.clock_out_at)}`
        );
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function submitLeaveRequest(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(`/employees/${DEMO_EMPLOYEE_ID}/leave-requests`, {
        method: "POST",
        body: JSON.stringify({ start_date: leaveStartDate, end_date: leaveEndDate }),
      });
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Leave request failed");
      } else {
        setMessage(`Leave request created for ${body.start_date} to ${body.end_date}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function approveLeaveRequest(leaveRequestId: string) {
    setBusy(true);

    try {
      const response = await apiRequest(
        `/leave-requests/${leaveRequestId}/approve`,
        { method: "POST" },
        { token: getManagerToken(), extraHeaders: { "x-role": "MANAGER" } }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Leave approval failed");
      } else {
        setMessage(`Leave request approved for ${body.start_date} to ${body.end_date}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function savePtoAdjustment(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(
        `/employees/${DEMO_EMPLOYEE_ID}/pto-adjustments`,
        {
          method: "POST",
          body: JSON.stringify({ days_delta: Number(ptoAdjustmentDays) }),
        },
        { token: getManagerToken(), extraHeaders: { "x-role": "MANAGER" } }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "PTO adjustment failed");
      } else {
        setMessage(`PTO adjusted by ${body.days_delta} day(s)`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function saveCompTimeAdjustment(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(
        `/employees/${DEMO_EMPLOYEE_ID}/comp-time-adjustments`,
        {
          method: "POST",
          body: JSON.stringify({
            minutes_delta: Number(compTimeAdjustmentMinutes),
            reason: compTimeAdjustmentReason,
          }),
        },
        { token: getManagerToken(), extraHeaders: { "x-role": "MANAGER" } }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Comp-time adjustment failed");
      } else {
        setMessage(`Comp-time adjusted by ${body.minutes_delta} minute(s)`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function submitScheduledShift(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(
        `/employees/${DEMO_EMPLOYEE_ID}/scheduled-shifts`,
        {
          method: "POST",
          body: JSON.stringify({
            start_at: scheduledStartAt,
            end_at: scheduledEndAt,
            break_minutes: Number(scheduledBreakMinutes),
          }),
        },
        { token: getManagerToken(), extraHeaders: { "x-role": "MANAGER" } }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Scheduling request failed");
      } else {
        setMessage(`Scheduled shift created for ${formatDate(body.start_at)} to ${formatDate(body.end_at)}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function savePolicyConfig(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(
        "/policies",
        {
          method: "PATCH",
          body: JSON.stringify({
            minimum_break_minutes: Number(policyDraft.minimum_break_minutes),
            core_hour_start: Number(policyDraft.core_hour_start),
            core_hour_end: Number(policyDraft.core_hour_end),
          }),
        },
        { token: getAdminToken(), extraHeaders: { "x-role": "ADMIN" } }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Policy update failed");
      } else {
        setMessage(`Policy updated: ${body.policies.minimum_break_minutes} min minimum break`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function saveEmployeeLocation(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(
        `/companies/${DEMO_COMPANY_ID}/employees/${selectedAdminEmployeeId}`,
        {
          method: "PATCH",
          body: JSON.stringify({ location_id: adminLocationId }),
        },
        { token: getAdminToken(), extraHeaders: ADMIN_HEADERS }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Location reassignment failed");
      } else {
        setMessage(`Employee ${body.employee_id} moved to ${body.location_id}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function saveNotificationSettings(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(
        `/companies/${DEMO_COMPANY_ID}/notification-settings`,
        {
          method: "PUT",
          body: JSON.stringify({
            destination_type: notificationDraft.destination_type,
            target: notificationDraft.target,
            secret_reference: notificationDraft.secret_reference,
            enabled: notificationDraft.enabled,
          }),
        },
        { token: getAdminToken(), extraHeaders: ADMIN_HEADERS }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Notification stub update failed");
      } else {
        setMessage(`Notification stub saved for ${body.destination_type}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function runNotificationTest() {
    setBusy(true);

    try {
      const response = await apiRequest(
        `/companies/${DEMO_COMPANY_ID}/notification-settings/test`,
        { method: "POST" },
        { token: getAdminToken(), extraHeaders: ADMIN_HEADERS }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Notification test failed");
      } else {
        setMessage(`Notification test simulated for ${body.target}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  async function saveSecretProvider(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const response = await apiRequest(
        `/companies/${DEMO_COMPANY_ID}/secret-provider`,
        {
          method: "PUT",
          body: JSON.stringify({
            provider: secretDraft.provider,
            reference_name: secretDraft.reference_name,
            enabled: secretDraft.enabled,
          }),
        },
        { token: getAdminToken(), extraHeaders: ADMIN_HEADERS }
      );
      const body = await response.json();

      if (!response.ok) {
        setMessage(body.detail ?? "Secret provider update failed");
      } else {
        setMessage(`Secret provider set to ${body.provider}`);
      }

      await refreshReadModels();
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Unexpected UI error";
      setMessage(fallback);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void refreshReadModels();
  }, []);

  useEffect(() => {
    if (shifts.length === 0) {
      return;
    }
    const latest = shifts[shifts.length - 1];
    setStatus(latest.state === "OPEN" ? "CLOCKED_IN" : "CLOCKED_OUT");
  }, [shifts]);

  useEffect(() => {
    if (!policyConfig) {
      return;
    }
    setPolicyDraft({
      minimum_break_minutes: String(policyConfig.minimum_break_minutes),
      core_hour_start: String(policyConfig.core_hour_start),
      core_hour_end: String(policyConfig.core_hour_end),
    });
  }, [policyConfig]);

  useEffect(() => {
    if (companyEmployees.length === 0) {
      return;
    }
    if (!companyEmployees.some((employee) => employee.employee_id === selectedAdminEmployeeId)) {
      setSelectedAdminEmployeeId(companyEmployees[0].employee_id);
    }
  }, [companyEmployees, selectedAdminEmployeeId]);

  useEffect(() => {
    const selectedEmployee = companyEmployees.find((employee) => employee.employee_id === selectedAdminEmployeeId);
    if (!selectedEmployee) {
      return;
    }
    setAdminLocationId(selectedEmployee.location_id);
  }, [companyEmployees, selectedAdminEmployeeId]);

  useEffect(() => {
    if (!notificationSettings) {
      return;
    }
    setNotificationDraft({
      destination_type: notificationSettings.destination_type,
      target: notificationSettings.target,
      secret_reference: notificationSettings.secret_reference ?? "",
      enabled: notificationSettings.enabled,
    });
  }, [notificationSettings]);

  useEffect(() => {
    if (!secretProvider) {
      return;
    }
    setSecretDraft({
      provider: secretProvider.provider,
      reference_name: secretProvider.reference_name,
      enabled: secretProvider.enabled,
    });
  }, [secretProvider]);

  useEffect(() => {
    if (!selectedPayrollLocationId) {
      return;
    }
    void refreshLocationPayrollExport(selectedPayrollLocationId);
  }, [selectedPayrollLocationId]);

  return (
    <main id="main-content" className="page" aria-labelledby="app-title">
      <a href="#main-content" className="skip-link">Skip to content</a>

      <section className="hero" aria-label="Application heading">
        <p className="eyebrow">Workforce Time Tracking & Payroll Integration Platform</p>
        <h1 id="app-title">Workforce Time Capture Console</h1>
        <p className="sub">Employee {DEMO_EMPLOYEE_ID} · {headerSub}</p>
      </section>

      <section className="controls card" aria-label="Punch controls">
        <div className="button-row">
          <button
            type="button"
            disabled={busy}
            aria-label={`Clock in employee ${DEMO_EMPLOYEE_ID}`}
            onClick={() => void runPunch("in")}
          >
            Clock In
          </button>
          <button
            type="button"
            className="secondary"
            disabled={busy}
            aria-label={`Clock out employee ${DEMO_EMPLOYEE_ID}`}
            onClick={() => void runPunch("out")}
          >
            Clock Out
          </button>
        </div>
        <p className="message" role="status" aria-live="polite">
          {message}
        </p>
      </section>

      <section className="grid">
        <article className="card">
          <h2>Shift History</h2>
          {shifts.length === 0 ? (
            <p className="empty">No shifts yet.</p>
          ) : (
            <ul className="list">
              {shifts
                .slice()
                .reverse()
                .map((shift) => (
                  <li key={shift.shift_id}>
                    <div>
                      <strong>{shift.state}</strong>
                      <span>
                        {formatDate(shift.start_at)} {" -> "} {formatDate(shift.end_at)}
                      </span>
                    </div>
                    <span>{shift.duration_minutes ?? 0} min</span>
                  </li>
                ))}
            </ul>
          )}
        </article>

        <article className="card">
          <h2>Payroll Summary</h2>
          {!summary ? (
            <p className="empty">No summary available.</p>
          ) : (
            <dl className="summary">
              <div>
                <dt>Total Minutes</dt>
                <dd>{summary.total_minutes_worked}</dd>
              </div>
              <div>
                <dt>Closed Shifts</dt>
                <dd>{summary.closed_shift_count}</dd>
              </div>
            </dl>
          )}
        </article>

        <article className="card">
          <h2>Payroll Breakdown</h2>
          {!payrollBreakdown ? (
            <p className="empty">No payroll breakdown available.</p>
          ) : (
            <dl className="summary">
              <div>
                <dt>Total Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.total_minutes_worked)}</dd>
              </div>
              <div>
                <dt>Regular Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.regular_minutes)}</dd>
              </div>
              <div>
                <dt>Overtime Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.overtime_minutes)}</dd>
              </div>
              <div>
                <dt>Holiday Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.holiday_minutes)}</dd>
              </div>
              <div>
                <dt>Night Shift Minutes</dt>
                <dd>{formatMinutes(payrollBreakdown.night_shift_minutes)}</dd>
              </div>
            </dl>
          )}
        </article>

        <article className="card compliance-card">
          <h2>Compliance Report</h2>
          {!complianceReport ? (
            <p className="empty">No compliance report available.</p>
          ) : (
            <div className="card-stack">
              <dl className="summary compliance-summary">
                <div>
                  <dt>Tax Validation Status</dt>
                  <dd>
                    <span className={getStatusClassName(complianceReport.tax_validation_status)}>
                      {complianceReport.tax_validation_status}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt>Labor Validation Status</dt>
                  <dd>
                    <span className={getStatusClassName(complianceReport.labor_rule_validation_status)}>
                      {complianceReport.labor_rule_validation_status}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt>Attendance Exceptions</dt>
                  <dd>{complianceReport.attendance_exception_count}</dd>
                </div>
              </dl>

              <div className="validation-columns">
                <section aria-label="Tax validations">
                  <p className="section-label">Tax Validations</p>
                  <ul className="list validation-list">
                    {complianceReport.tax_validations.map((validation) => (
                      <li key={validation.rule}>
                        <div>
                          <strong>{formatRuleLabel(validation.rule)}</strong>
                          <span>{validation.details}</span>
                        </div>
                        <span className={getStatusClassName(validation.status)}>{validation.status}</span>
                      </li>
                    ))}
                  </ul>
                </section>

                <section aria-label="Labor validations">
                  <p className="section-label">Labor Validations</p>
                  <ul className="list validation-list">
                    {complianceReport.labor_rule_validations.map((validation) => (
                      <li key={validation.rule}>
                        <div>
                          <strong>{formatRuleLabel(validation.rule)}</strong>
                          <span>{validation.details}</span>
                        </div>
                        <span className={getStatusClassName(validation.status)}>{validation.status}</span>
                      </li>
                    ))}
                  </ul>
                </section>
              </div>
            </div>
          )}
        </article>
      </section>

      <section className="card leave-card">
        <h2>Leave Workflow</h2>
        <form className="leave-form" onSubmit={(event) => void submitLeaveRequest(event)}>
          <label>
            <span>Leave start date</span>
            <input
              type="date"
              value={leaveStartDate}
              onChange={(event) => setLeaveStartDate(event.target.value)}
            />
          </label>
          <label>
            <span>Leave end date</span>
            <input
              type="date"
              value={leaveEndDate}
              onChange={(event) => setLeaveEndDate(event.target.value)}
            />
          </label>
          <button type="submit" disabled={busy}>
            Submit Leave Request
          </button>
        </form>

        {leaveBalance ? (
          <dl className="summary leave-summary">
            <div>
              <dt>Total Days</dt>
              <dd>{leaveBalance.total_days}</dd>
            </div>
            <div>
              <dt>Used Days</dt>
              <dd>{leaveBalance.used_days}</dd>
            </div>
            <div>
              <dt>Remaining Days</dt>
              <dd>{leaveBalance.remaining_days}</dd>
            </div>
          </dl>
        ) : (
          <p className="empty">No leave balance available.</p>
        )}

        {leaveRequests.length === 0 ? (
          <p className="empty">No leave requests yet.</p>
        ) : (
          <ul className="list leave-list">
            {leaveRequests
              .slice()
              .reverse()
              .map((request) => (
                <li key={request.leave_request_id} data-leave-request-id={request.leave_request_id}>
                  <div>
                    <strong>{request.status}</strong>
                    <span>
                      {request.start_date} to {request.end_date}
                    </span>
                  </div>
                  {request.status === "PENDING" ? (
                    <button
                      type="button"
                      className="secondary"
                      disabled={busy}
                      onClick={() => void approveLeaveRequest(request.leave_request_id)}
                    >
                      Approve Leave Request
                    </button>
                  ) : (
                    <span>{request.approved_at ? `Approved ${formatDate(request.approved_at)}` : "Approved"}</span>
                  )}
                </li>
              ))}
          </ul>
        )}
      </section>

      <section className="card compensation-card">
        <h2>Compensation & Integration</h2>
        <div className="card-stack reporting-stack">
          <article className="nested-card" aria-label="PTO balance and adjustments">
            <h3>PTO Management</h3>
            {!ptoBalance ? (
              <p className="empty">No PTO balance available.</p>
            ) : (
              <dl className="summary">
                <div>
                  <dt>Total Days</dt>
                  <dd>{ptoBalance.total_days}</dd>
                </div>
                <div>
                  <dt>Used Days</dt>
                  <dd>{ptoBalance.used_days}</dd>
                </div>
                <div>
                  <dt>Remaining Days</dt>
                  <dd>{ptoBalance.remaining_days}</dd>
                </div>
              </dl>
            )}
            <form className="nested-form" onSubmit={(event) => void savePtoAdjustment(event)}>
              <label>
                <span>PTO adjustment days</span>
                <input
                  type="number"
                  step="1"
                  value={ptoAdjustmentDays}
                  onChange={(event) => setPtoAdjustmentDays(event.target.value)}
                />
              </label>
              <button type="submit" disabled={busy}>Adjust PTO Balance</button>
            </form>
          </article>

          <article className="nested-card" aria-label="Comp-time balance and adjustments">
            <h3>Comp-Time Management</h3>
            {!compTimeBalance ? (
              <p className="empty">No comp-time balance available.</p>
            ) : (
              <dl className="summary">
                <div>
                  <dt>Accrued From Overtime</dt>
                  <dd>{formatMinutes(compTimeBalance.accrued_from_overtime_minutes)}</dd>
                </div>
                <div>
                  <dt>Manual Adjustment</dt>
                  <dd>{formatMinutes(compTimeBalance.manual_adjustment_minutes)}</dd>
                </div>
                <div>
                  <dt>Total Comp Time</dt>
                  <dd>{formatMinutes(compTimeBalance.total_comp_time_minutes)}</dd>
                </div>
              </dl>
            )}
            <form className="nested-form" onSubmit={(event) => void saveCompTimeAdjustment(event)}>
              <label>
                <span>Comp-time adjustment minutes</span>
                <input
                  type="number"
                  step="1"
                  value={compTimeAdjustmentMinutes}
                  onChange={(event) => setCompTimeAdjustmentMinutes(event.target.value)}
                />
              </label>
              <label>
                <span>Adjustment reason</span>
                <input
                  type="text"
                  value={compTimeAdjustmentReason}
                  onChange={(event) => setCompTimeAdjustmentReason(event.target.value)}
                />
              </label>
              <button type="submit" disabled={busy}>Adjust Comp Time</button>
            </form>
          </article>

          <article className="nested-card" aria-label="Payroll integration payload">
            <h3>Payroll Integration Payload</h3>
            {!payrollIntegrationPayload ? (
              <p className="empty">No payroll integration payload available.</p>
            ) : (
              <div className="card-stack">
                <dl className="summary">
                  <div>
                    <dt>Schema Version</dt>
                    <dd>{payrollIntegrationPayload.schema_version}</dd>
                  </div>
                  <div>
                    <dt>Destination</dt>
                    <dd>{payrollIntegrationPayload.destination}</dd>
                  </div>
                  <div>
                    <dt>Employee Rows</dt>
                    <dd>{payrollIntegrationPayload.employees.length}</dd>
                  </div>
                  <div>
                    <dt>Generated</dt>
                    <dd>{formatDate(payrollIntegrationPayload.generated_at)}</dd>
                  </div>
                </dl>
                {payrollIntegrationPayload.employees.length === 0 ? (
                  <p className="empty">No payroll integration rows available.</p>
                ) : (
                  <ul className="list">
                    {payrollIntegrationPayload.employees.map((row) => (
                      <li key={`${row.employee_id}-${row.location_id}`}>
                        <div>
                          <strong>{row.employee_id}</strong>
                          <span>{row.location_id}</span>
                          <span>
                            Total {formatMinutes(row.total_minutes_worked)} · OT {formatMinutes(row.overtime_minutes)}
                          </span>
                        </div>
                        <span>{formatMinutes(row.holiday_minutes + row.night_shift_minutes)} premium time</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </article>
        </div>
      </section>

      <section className="card scheduling-card">
        <h2>Scheduling Workflow</h2>
        <form className="schedule-form" onSubmit={(event) => void submitScheduledShift(event)}>
          <label>
            <span>Scheduled start</span>
            <input
              type="datetime-local"
              value={scheduledStartAt}
              onChange={(event) => setScheduledStartAt(event.target.value)}
            />
          </label>
          <label>
            <span>Scheduled end</span>
            <input
              type="datetime-local"
              value={scheduledEndAt}
              onChange={(event) => setScheduledEndAt(event.target.value)}
            />
          </label>
          <label>
            <span>Break minutes</span>
            <input
              type="number"
              min={policyConfig?.minimum_break_minutes ?? 1}
              step="1"
              value={scheduledBreakMinutes}
              onChange={(event) => setScheduledBreakMinutes(event.target.value)}
            />
          </label>
          <button type="submit" disabled={busy}>
            Schedule Shift
          </button>
        </form>

        {policyConfig ? (
          <dl className="summary schedule-policy-summary">
            <div>
              <dt>Minimum Break</dt>
              <dd>{policyConfig.minimum_break_minutes} min</dd>
            </div>
            <div>
              <dt>Core Hours</dt>
              <dd>
                {policyConfig.core_hour_start}:00 - {policyConfig.core_hour_end}:00
              </dd>
            </div>
          </dl>
        ) : (
          <p className="empty">Policy guidance unavailable.</p>
        )}

        {scheduledShifts.length === 0 ? (
          <p className="empty">No scheduled shifts yet.</p>
        ) : (
          <ul className="list schedule-list">
            {scheduledShifts
              .slice()
              .reverse()
              .map((shift) => (
                <li key={shift.scheduled_shift_id}>
                  <div>
                    <strong>{shift.status}</strong>
                    <span>
                      {formatDate(shift.start_at)} {" -> "} {formatDate(shift.end_at)}
                    </span>
                    <span>
                      Break {shift.break_minutes} min · Core hours {shift.covers_core_hours ? "covered" : "missed"}
                    </span>
                  </div>
                  <span>{shift.break_compliant ? "Break compliant" : "Break issue"}</span>
                </li>
              ))}
          </ul>
        )}
      </section>

      <section className="card admin-card">
        <h2>Enterprise Admin Overview</h2>
        <p className="section-label">Company {DEMO_COMPANY_ID}</p>

        <div className="card-stack admin-stack">
          <article className="nested-card" aria-label="Company employee directory">
            <h3>Company Directory</h3>
            {companyEmployees.length === 0 ? (
              <p className="empty">No company employees available.</p>
            ) : (
              <ul className="list">
                {companyEmployees.map((employee) => (
                  <li key={employee.employee_id}>
                    <div>
                      <strong>{employee.employee_id}</strong>
                      <span>{employee.company_id}</span>
                    </div>
                    <span>{employee.location_id}</span>
                  </li>
                ))}
              </ul>
            )}
          </article>

          <article className="nested-card" aria-label="Company location overview">
            <h3>Location Coverage</h3>
            {companyLocations.length === 0 ? (
              <p className="empty">No company locations available.</p>
            ) : (
              <ul className="list">
                {companyLocations.map((location) => (
                  <li key={location.location_id}>
                    <div>
                      <strong>{location.location_id}</strong>
                      <span>Assigned employees</span>
                    </div>
                    <span>{location.employee_count}</span>
                  </li>
                ))}
              </ul>
            )}
          </article>

          <article className="nested-card" aria-label="Policy controls">
            <h3>Policy Controls</h3>
            <form className="nested-form" onSubmit={(event) => void savePolicyConfig(event)}>
              <label>
                <span>Minimum break minutes</span>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={policyDraft.minimum_break_minutes}
                  onChange={(event) =>
                    setPolicyDraft((current) => ({ ...current, minimum_break_minutes: event.target.value }))
                  }
                />
              </label>
              <label>
                <span>Core hour start</span>
                <input
                  type="number"
                  min="0"
                  max="23"
                  step="1"
                  value={policyDraft.core_hour_start}
                  onChange={(event) =>
                    setPolicyDraft((current) => ({ ...current, core_hour_start: event.target.value }))
                  }
                />
              </label>
              <label>
                <span>Core hour end</span>
                <input
                  type="number"
                  min="1"
                  max="24"
                  step="1"
                  value={policyDraft.core_hour_end}
                  onChange={(event) =>
                    setPolicyDraft((current) => ({ ...current, core_hour_end: event.target.value }))
                  }
                />
              </label>
              <button type="submit" disabled={busy}>Save Policy Settings</button>
            </form>
          </article>

          <article className="nested-card" aria-label="Location assignment workflow">
            <h3>Location Assignment</h3>
            <form className="nested-form" onSubmit={(event) => void saveEmployeeLocation(event)}>
              <label>
                <span>Employee</span>
                <select
                  value={selectedAdminEmployeeId}
                  onChange={(event) => setSelectedAdminEmployeeId(event.target.value)}
                >
                  {companyEmployees.map((employee) => (
                    <option key={employee.employee_id} value={employee.employee_id}>
                      {employee.employee_id}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Assigned location</span>
                <input
                  type="text"
                  value={adminLocationId}
                  onChange={(event) => setAdminLocationId(event.target.value.toUpperCase())}
                />
              </label>
              <button type="submit" disabled={busy || companyEmployees.length === 0}>Save Location Assignment</button>
            </form>
          </article>

          <article className="nested-card" aria-label="Notification stub settings">
            <h3>Notification Stub</h3>
            <form className="nested-form" onSubmit={(event) => void saveNotificationSettings(event)}>
              <label>
                <span>Destination type</span>
                <select
                  value={notificationDraft.destination_type}
                  onChange={(event) =>
                    setNotificationDraft((current) => ({ ...current, destination_type: event.target.value }))
                  }
                >
                  <option value="WEBHOOK">WEBHOOK</option>
                  <option value="EMAIL">EMAIL</option>
                  <option value="SLACK_STUB">SLACK_STUB</option>
                </select>
              </label>
              <label>
                <span>Target</span>
                <input
                  type="text"
                  value={notificationDraft.target}
                  onChange={(event) =>
                    setNotificationDraft((current) => ({ ...current, target: event.target.value }))
                  }
                />
              </label>
              <label>
                <span>Secret reference</span>
                <input
                  type="text"
                  value={notificationDraft.secret_reference}
                  onChange={(event) =>
                    setNotificationDraft((current) => ({ ...current, secret_reference: event.target.value }))
                  }
                />
              </label>
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={notificationDraft.enabled}
                  onChange={(event) =>
                    setNotificationDraft((current) => ({ ...current, enabled: event.target.checked }))
                  }
                />
                <span>Enable downstream notification stub</span>
              </label>
              <div className="inline-actions">
                <button type="submit" disabled={busy}>Save Notification Stub</button>
                <button type="button" className="secondary" disabled={busy} onClick={() => void runNotificationTest()}>
                  Run Notification Test
                </button>
              </div>
            </form>
            {notificationSettings ? (
              <p className="helper-copy">
                Status {notificationSettings.status} · Mode {notificationSettings.delivery_mode}
                {notificationSettings.last_tested_at ? ` · Last test ${formatDate(notificationSettings.last_tested_at)}` : ""}
              </p>
            ) : null}
          </article>

          <article className="nested-card" aria-label="Secret provider settings">
            <h3>Secret Provider Stub</h3>
            <form className="nested-form" onSubmit={(event) => void saveSecretProvider(event)}>
              <label>
                <span>Provider</span>
                <select
                  value={secretDraft.provider}
                  onChange={(event) =>
                    setSecretDraft((current) => ({ ...current, provider: event.target.value }))
                  }
                >
                  <option value="ENV">ENV</option>
                  <option value="VAULT_STUB">VAULT_STUB</option>
                  <option value="KMS_STUB">KMS_STUB</option>
                </select>
              </label>
              <label>
                <span>Reference name</span>
                <input
                  type="text"
                  value={secretDraft.reference_name}
                  onChange={(event) =>
                    setSecretDraft((current) => ({ ...current, reference_name: event.target.value }))
                  }
                />
              </label>
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={secretDraft.enabled}
                  onChange={(event) =>
                    setSecretDraft((current) => ({ ...current, enabled: event.target.checked }))
                  }
                />
                <span>Enable secret-provider stub</span>
              </label>
              <button type="submit" disabled={busy}>Save Secret Provider</button>
            </form>
            {secretProvider ? (
              <p className="helper-copy">
                Status {secretProvider.status} · Raw secret values are never stored in this demo
              </p>
            ) : null}
          </article>
        </div>
      </section>

      <section className="card reporting-card">
        <h2>Operational Reporting</h2>
        <div className="card-stack reporting-stack">
          <article className="nested-card" aria-label="Operational report summary">
            <h3>Operational Summary</h3>
            {!operationalReport ? (
              <p className="empty">No operational report available.</p>
            ) : (
              <dl className="summary operational-summary">
                <div>
                  <dt>Accepted Events</dt>
                  <dd>{operationalReport.accepted_event_count}</dd>
                </div>
                <div>
                  <dt>Rejected Events</dt>
                  <dd>{operationalReport.rejected_event_count}</dd>
                </div>
                <div>
                  <dt>Open Shifts</dt>
                  <dd>{operationalReport.open_shift_count}</dd>
                </div>
                <div>
                  <dt>Closed Shifts</dt>
                  <dd>{operationalReport.closed_shift_count}</dd>
                </div>
              </dl>
            )}
          </article>

          <article className="nested-card" aria-label="Crosscheck report summary">
            <h3>CrossCheck Summary</h3>
            {!crosscheckReport ? (
              <p className="empty">No crosscheck report available.</p>
            ) : (
              <div className="card-stack">
                <dl className="summary">
                  <div>
                    <dt>Employee</dt>
                    <dd>{crosscheckReport.employee_id}</dd>
                  </div>
                  <div>
                    <dt>Payroll Minutes</dt>
                    <dd>{crosscheckReport.payroll_summary_total_minutes}</dd>
                  </div>
                  <div>
                    <dt>Derived Minutes</dt>
                    <dd>{crosscheckReport.derived_shift_total_minutes}</dd>
                  </div>
                </dl>
                <p className="inline-status">
                  <span className={getStatusClassName(crosscheckReport.status === "MATCH" ? "PASS" : "FAIL")}>
                    {crosscheckReport.status}
                  </span>
                </p>
              </div>
            )}
          </article>

          <article className="nested-card" aria-label="Payroll export status">
            <h3>Payroll Export Readiness</h3>
            {!payrollExport ? (
              <p className="empty">No payroll export available.</p>
            ) : (
              <dl className="summary">
                <div>
                  <dt>Status</dt>
                  <dd>{payrollExport.status}</dd>
                </div>
                <div>
                  <dt>Employee Rows</dt>
                  <dd>{payrollExport.row_count}</dd>
                </div>
                <div>
                  <dt>Generated</dt>
                  <dd>{formatDate(payrollExport.generated_at)}</dd>
                </div>
              </dl>
            )}
          </article>

          <article className="nested-card" aria-label="Location payroll export status">
            <h3>Location Payroll Export</h3>
            <form className="nested-form" onSubmit={(event) => event.preventDefault()}>
              <label>
                <span>Location</span>
                <select
                  value={selectedPayrollLocationId}
                  onChange={(event) => setSelectedPayrollLocationId(event.target.value)}
                >
                  {companyLocations.map((location) => (
                    <option key={location.location_id} value={location.location_id}>
                      {location.location_id}
                    </option>
                  ))}
                </select>
              </label>
            </form>
            {!locationPayrollExport ? (
              <p className="empty">No location payroll export available.</p>
            ) : (
              <dl className="summary">
                <div>
                  <dt>Status</dt>
                  <dd>{locationPayrollExport.status}</dd>
                </div>
                <div>
                  <dt>Location</dt>
                  <dd>{locationPayrollExport.location_id ?? selectedPayrollLocationId}</dd>
                </div>
                <div>
                  <dt>Employee Rows</dt>
                  <dd>{locationPayrollExport.row_count}</dd>
                </div>
                <div>
                  <dt>Generated</dt>
                  <dd>{formatDate(locationPayrollExport.generated_at)}</dd>
                </div>
              </dl>
            )}
          </article>
        </div>
      </section>

      <section className="card">
        <h2>Audit Events</h2>
        {events.length === 0 ? (
          <p className="empty">No audit events yet.</p>
        ) : (
          <ul className="list">
            {events
              .slice()
              .reverse()
              .map((event) => (
                <li key={event.event_id}>
                  <div>
                    <strong>{event.event_type}</strong>
                    <span>{formatDate(event.event_at)}</span>
                  </div>
                  <span>{event.details}</span>
                </li>
              ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h2>Missing Punch Exceptions</h2>
        {exceptions.length === 0 ? (
          <p className="empty">No missing punch exceptions.</p>
        ) : (
          <ul className="list">
            {exceptions.map((exception) => (
              <li key={exception.shift_id}>
                <div>
                  <strong>{exception.status}</strong>
                  <span>Shift {exception.shift_id}</span>
                </div>
                <span>{exception.elapsed_minutes} min open</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
