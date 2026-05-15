import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const originalFetch = globalThis.fetch;

type MockResponder = (input: RequestInfo | URL, init?: RequestInit) => Response | Promise<Response>;

type MockRoute = {
  method: string;
  path: string;
  response: Response | MockResponder;
};

function jsonResponse(body: unknown, ok = true, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function route(method: string, path: string, response: MockRoute["response"]): MockRoute {
  return { method, path, response };
}

function requestPath(input: RequestInfo | URL): string {
  const url = new URL(String(input), "http://127.0.0.1");
  return `${url.pathname}${url.search}`;
}

function parseJsonBody(init?: RequestInit): Record<string, unknown> {
  return JSON.parse(String(init?.body ?? "{}")) as Record<string, unknown>;
}

function buildBootstrapRoutes(): MockRoute[] {
  return [
    route("GET", "/employees/E001/shifts", jsonResponse({ shifts: [] })),
    route("GET", "/employees/E001/audit-events", jsonResponse({ events: [] })),
    route(
      "GET",
      "/employees/E001/payroll-summary",
      jsonResponse({
        employee_id: "E001",
        total_minutes_worked: 0,
        closed_shift_count: 0,
        period_start: null,
        period_end: null,
      })
    ),
    route(
      "GET",
      "/employees/E001/payroll-breakdown",
      jsonResponse({
        employee_id: "E001",
        total_minutes_worked: 0,
        regular_minutes: 0,
        overtime_minutes: 0,
        holiday_minutes: 0,
        night_shift_minutes: 0,
      })
    ),
    route(
      "GET",
      "/employees/E001/compliance-report",
      jsonResponse({
        employee_id: "E001",
        tax_validation_status: "WARN",
        labor_rule_validation_status: "PASS",
        attendance_exception_count: 0,
        tax_validations: [],
        labor_rule_validations: [],
      })
    ),
    route(
      "GET",
      "/employees/E001/missing-punch-exceptions?threshold_minutes=60",
      jsonResponse({ exceptions: [], threshold_minutes: 60 })
    ),
    route("GET", "/employees/E001/leave-requests", jsonResponse({ leave_requests: [] })),
    route(
      "GET",
      "/employees/E001/leave-balance",
      jsonResponse({ employee_id: "E001", total_days: 20, used_days: 0, remaining_days: 20 })
    ),
    route(
      "GET",
      "/employees/E001/pto-balance",
      jsonResponse({ employee_id: "E001", total_days: 20, used_days: 0, remaining_days: 20 })
    ),
    route(
      "GET",
      "/employees/E001/comp-time-balance",
      jsonResponse({
        employee_id: "E001",
        accrued_from_overtime_minutes: 0,
        manual_adjustment_minutes: 0,
        total_comp_time_minutes: 0,
      })
    ),
    route("GET", "/employees/E001/scheduled-shifts", jsonResponse({ scheduled_shifts: [] })),
    route(
      "GET",
      "/policies",
      jsonResponse({ policies: { minimum_break_minutes: 30, core_hour_start: 10, core_hour_end: 15 } })
    ),
    route(
      "GET",
      "/companies/COMP-001/employees",
      jsonResponse({
        employees: [{ employee_id: "E001", company_id: "COMP-001", location_id: "LOC-001" }],
      })
    ),
    route(
      "GET",
      "/companies/COMP-001/locations",
      jsonResponse({
        company_id: "COMP-001",
        locations: [{ location_id: "LOC-001", employee_count: 1 }],
      })
    ),
    route(
      "GET",
      "/reports/operational?company_id=COMP-001",
      jsonResponse({
        company_id: "COMP-001",
        event_count: 0,
        accepted_event_count: 0,
        rejected_event_count: 0,
        open_shift_count: 0,
        closed_shift_count: 0,
      })
    ),
    route(
      "GET",
      "/reports/crosscheck?employee_id=E001",
      jsonResponse({
        employee_id: "E001",
        payroll_summary_total_minutes: 0,
        derived_shift_total_minutes: 0,
        status: "MATCH",
      })
    ),
    route(
      "GET",
      "/companies/COMP-001/payroll-export",
      jsonResponse({
        company_id: "COMP-001",
        generated_at: "2026-05-15T12:00:00+00:00",
        row_count: 1,
        status: "READY",
      })
    ),
    route(
      "GET",
      "/companies/COMP-001/locations/LOC-001/payroll-export",
      jsonResponse({
        company_id: "COMP-001",
        location_id: "LOC-001",
        generated_at: "2026-05-15T12:00:00+00:00",
        row_count: 1,
        status: "READY",
      })
    ),
    route(
      "GET",
      "/companies/COMP-001/payroll-integration-payload",
      jsonResponse({
        company_id: "COMP-001",
        generated_at: "2026-05-15T12:00:00+00:00",
        schema_version: "1.0",
        destination: "future-payroll-integration",
        employees: [
          {
            employee_id: "E001",
            location_id: "LOC-001",
            total_minutes_worked: 0,
            overtime_minutes: 0,
            holiday_minutes: 0,
            night_shift_minutes: 0,
          },
        ],
      })
    ),
    route(
      "GET",
      "/companies/COMP-001/notification-settings",
      jsonResponse({
        company_id: "COMP-001",
        destination_type: "WEBHOOK",
        target: "",
        secret_reference: null,
        enabled: false,
        status: "NOT_CONFIGURED",
        last_tested_at: null,
        delivery_mode: "STUB",
      })
    ),
    route(
      "GET",
      "/companies/COMP-001/secret-provider",
      jsonResponse({
        company_id: "COMP-001",
        provider: "ENV",
        reference_name: "",
        enabled: false,
        status: "NOT_CONFIGURED",
        stores_secret_material: false,
        updated_at: null,
      })
    ),
  ];
}

function installApiMock(routes: MockRoute[]): void {
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const method = (init?.method ?? "GET").toUpperCase();
    const path = requestPath(input);

    for (let index = routes.length - 1; index >= 0; index -= 1) {
      const candidate = routes[index];
      if (candidate.method === method && candidate.path === path) {
        if (typeof candidate.response === "function") {
          return await candidate.response(input, init);
        }
        return candidate.response.clone();
      }
    }

    throw new Error(`Unhandled request: ${method} ${path}`);
  }) as typeof fetch;
}

// These are narrow component tests with mocked transport. Backend/API correctness is covered elsewhere.
describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("renders the shell and initial location-scoped export state", async () => {
    installApiMock(buildBootstrapRoutes());

    render(<App />);

    expect(screen.getByRole("heading", { name: "Workforce Time Capture Console" })).toBeVisible();

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Location Payroll Export" })).toBeVisible();
    });

    const locationExportCard = screen.getByLabelText("Location payroll export status");
    expect(screen.getByText("No shifts yet.")).toBeVisible();
    expect(within(locationExportCard).getByDisplayValue("LOC-001")).toBeVisible();
    expect(within(locationExportCard).getByText("READY")).toBeVisible();
  });

  it("surfaces backend error details for failed punch attempts", async () => {
    installApiMock([
      ...buildBootstrapRoutes(),
      route("POST", "/employees/E001/clock-in", jsonResponse({ detail: "Invalid bearer token" }, false, 401)),
    ]);

    const user = userEvent.setup();
    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Scheduling Workflow" })).toBeVisible();
    });

    await user.click(screen.getByRole("button", { name: "Clock in employee E001" }));

    await waitFor(() => {
      expect(screen.getByText("Invalid bearer token")).toBeVisible();
    });
  });

  it("refetches the location-scoped payroll export when the selected location changes", async () => {
    const requestedPaths: string[] = [];

    installApiMock([
      ...buildBootstrapRoutes(),
      route(
        "GET",
        "/companies/COMP-001/locations",
        jsonResponse({
          company_id: "COMP-001",
          locations: [
            { location_id: "LOC-001", employee_count: 1 },
            { location_id: "LOC-002", employee_count: 1 },
          ],
        })
      ),
      route(
        "GET",
        "/companies/COMP-001/locations/LOC-001/payroll-export",
        jsonResponse({
          company_id: "COMP-001",
          location_id: "LOC-001",
          generated_at: "2026-05-15T12:00:00+00:00",
          row_count: 1,
          status: "READY",
        })
      ),
      route(
        "GET",
        "/companies/COMP-001/locations/LOC-002/payroll-export",
        (input) => {
          requestedPaths.push(requestPath(input));
          return jsonResponse({
            company_id: "COMP-001",
            location_id: "LOC-002",
            generated_at: "2026-05-15T12:05:00+00:00",
            row_count: 2,
            status: "READY",
          });
        }
      ),
    ]);

    const user = userEvent.setup();
    render(<App />);

    await waitFor(() => {
      expect(screen.getByLabelText("Location payroll export status")).toBeVisible();
    });

    const locationExportCard = screen.getByLabelText("Location payroll export status");
    await user.selectOptions(within(locationExportCard).getByLabelText("Location"), "LOC-002");

    await waitFor(() => {
      expect(within(locationExportCard).getByDisplayValue("LOC-002")).toBeVisible();
    });
    expect(within(locationExportCard).getByText("2")).toBeVisible();
    expect(requestedPaths).toContain("/companies/COMP-001/locations/LOC-002/payroll-export");
  });

  it("submits compensation adjustments with the expected payloads and refreshes the visible balances", async () => {
    let ptoBalance = { employee_id: "E001", total_days: 20, used_days: 0, remaining_days: 20 };
    let compTimeBalance = {
      employee_id: "E001",
      accrued_from_overtime_minutes: 60,
      manual_adjustment_minutes: 0,
      total_comp_time_minutes: 60,
    };
    let capturedPtoBody: Record<string, unknown> | null = null;
    let capturedCompBody: Record<string, unknown> | null = null;

    installApiMock([
      ...buildBootstrapRoutes(),
      route(
        "GET",
        "/employees/E001/pto-balance",
        () => jsonResponse(ptoBalance)
      ),
      route(
        "GET",
        "/employees/E001/comp-time-balance",
        () => jsonResponse(compTimeBalance)
      ),
      route(
        "POST",
        "/employees/E001/pto-adjustments",
        (_input, init) => {
          capturedPtoBody = parseJsonBody(init);
          const daysDelta = Number(capturedPtoBody.days_delta ?? 0);
          ptoBalance = {
            ...ptoBalance,
            total_days: ptoBalance.total_days + daysDelta,
            remaining_days: ptoBalance.remaining_days + daysDelta,
          };
          return jsonResponse({ days_delta: daysDelta });
        }
      ),
      route(
        "POST",
        "/employees/E001/comp-time-adjustments",
        (_input, init) => {
          capturedCompBody = parseJsonBody(init);
          const minutesDelta = Number(capturedCompBody.minutes_delta ?? 0);
          compTimeBalance = {
            ...compTimeBalance,
            manual_adjustment_minutes: compTimeBalance.manual_adjustment_minutes + minutesDelta,
            total_comp_time_minutes: compTimeBalance.total_comp_time_minutes + minutesDelta,
          };
          return jsonResponse({ minutes_delta: minutesDelta, reason: capturedCompBody.reason });
        }
      ),
    ]);

    const user = userEvent.setup();
    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Compensation & Integration" })).toBeVisible();
    });

    const ptoCard = screen.getByLabelText("PTO balance and adjustments");
    const compTimeCard = screen.getByLabelText("Comp-time balance and adjustments");
    await user.clear(within(ptoCard).getByLabelText("PTO adjustment days"));
    await user.type(within(ptoCard).getByLabelText("PTO adjustment days"), "2");
    await user.click(within(ptoCard).getByRole("button", { name: "Adjust PTO Balance" }));

    await waitFor(() => {
      expect(screen.getByText("PTO adjusted by 2 day(s)")).toBeVisible();
    });

    await user.clear(within(compTimeCard).getByLabelText("Comp-time adjustment minutes"));
    await user.type(within(compTimeCard).getByLabelText("Comp-time adjustment minutes"), "30");
    await user.clear(within(compTimeCard).getByLabelText("Adjustment reason"));
    await user.type(within(compTimeCard).getByLabelText("Adjustment reason"), "Manual correction");
    await user.click(within(compTimeCard).getByRole("button", { name: "Adjust Comp Time" }));

    await waitFor(() => {
      expect(screen.getByText("Comp-time adjusted by 30 minute(s)")).toBeVisible();
    });

    expect(capturedPtoBody).toEqual({ days_delta: 2 });
    expect(capturedCompBody).toEqual({ minutes_delta: 30, reason: "Manual correction" });
    expect(within(ptoCard).getAllByText("22")).toHaveLength(2);
    expect(within(compTimeCard).getByText("90 min")).toBeVisible();
  });
});