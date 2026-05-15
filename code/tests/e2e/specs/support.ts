import { expect, type APIRequestContext } from "@playwright/test";

const testSupportHeaders = {
  "x-test-support-token": process.env.PW_TEST_SUPPORT_TOKEN ?? "buildathon-e2e",
};

export async function resetDemoState(request: APIRequestContext) {
  const response = await request.post("http://127.0.0.1:8000/test-support/reset", {
    headers: testSupportHeaders,
  });

  expect(response.status()).toBe(200);
}