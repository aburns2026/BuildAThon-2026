import { expect, test, type APIRequestContext } from "@playwright/test";

const authHeader = {
  Authorization: `Bearer ${process.env.PW_DEMO_AUTH_TOKEN ?? "demo-employee-token"}`,
};

async function ensureNoOpenShift(request: APIRequestContext) {
  const response = await request.post("http://127.0.0.1:8000/employees/E001/clock-out", {
    headers: authHeader,
  });
  if (![200, 409].includes(response.status())) {
    throw new Error(`Unexpected preflight clock-out status: ${response.status()}`);
  }
}

test("Accessibility pack: landmarks and names are present", async ({ page, request }) => {
  await ensureNoOpenShift(request);
  await page.goto("/");

  await expect(page.getByRole("main", { name: "Workforce Time Capture Console" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 1, name: "Workforce Time Capture Console" })).toBeVisible();
  await expect(page.getByRole("region", { name: "Punch controls" })).toBeVisible();

  await expect(page.getByRole("button", { name: "Clock in employee E001" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Clock out employee E001" })).toBeVisible();
  await expect(page.getByLabel("Leave start date")).toBeVisible();
  await expect(page.getByLabel("Leave end date")).toBeVisible();
  await expect(page.getByRole("button", { name: "Submit Leave Request" })).toBeVisible();
  await expect(page.getByLabel("Scheduled start")).toBeVisible();
  await expect(page.getByLabel("Scheduled end")).toBeVisible();
  await expect(page.getByLabel("Break minutes")).toBeVisible();
  await expect(page.getByRole("button", { name: "Schedule Shift" })).toBeVisible();

  const status = page.locator("p.message");
  await expect(status).toHaveAttribute("role", "status");
  await expect(status).toHaveAttribute("aria-live", "polite");
});

test("Accessibility pack: keyboard-only punch interaction", async ({ page, request }) => {
  await ensureNoOpenShift(request);
  await page.goto("/");

  const clockIn = page.getByRole("button", { name: "Clock in employee E001" });
  await clockIn.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("p.message")).toContainText("Clock-in accepted");

  const clockOut = page.getByRole("button", { name: "Clock out employee E001" });
  await expect(clockOut).toBeEnabled();
  await clockOut.focus();
  await expect(clockOut).toBeFocused();
  await clockOut.press("Space");
  await expect(page.locator("p.message")).toContainText("Clock-out accepted");
});

test("Accessibility pack: skip link and headings remain usable", async ({ page, request }) => {
  await ensureNoOpenShift(request);
  await page.goto("/");

  await page.keyboard.press("Tab");
  const skipLink = page.getByRole("link", { name: "Skip to content" });
  await expect(skipLink).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(skipLink).toHaveAttribute("href", "#main-content");

  const headings = page.getByRole("heading");
  await expect(headings).toHaveCount(9);
  await expect(page.getByRole("heading", { level: 2, name: "Shift History" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Payroll Summary" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Payroll Breakdown" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Compliance Report" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Leave Workflow" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Scheduling Workflow" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Audit Events" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Missing Punch Exceptions" })).toBeVisible();
});
