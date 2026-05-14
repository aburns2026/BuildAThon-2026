# BugBot Output (Step 7)

Date: 2026-05-14
Defect Type: UI test strict-mode selector collision

## 1. Bug Summary

Playwright E2E test failed on assertion for "Clock-out accepted" because selector matched two elements in strict mode.

## 2. Reproduction Steps

1. Run E2E test suite in `code/tests/e2e`.
2. Execute `npm test`.
3. Observe failure where `getByText("Clock-out accepted")` resolves multiple elements.

## 3. Probable Root Causes

- Generic text selector matched both status message and audit list content.
- Strict mode requires a unique target element.

## 4. Smallest Fix Plan

- Scope status assertions to the UI message element (`p.message`) instead of global text query.
- Keep audit-event assertions separate for audit section validation.

## 5. Verification Plan

1. Re-run `npm test` in `code/tests/e2e`.
2. Confirm test passes for:
   - clock-in success message
   - duplicate validation message
   - clock-out success message
   - history, payroll summary, and audit visibility checks

## 6. Residual Risks

- Future text duplication may reintroduce ambiguity if selectors are broad.
- Keep selectors anchored to role/region/message container for reliability.

## Evidence Reference

- Updated file: `code/tests/e2e/specs/main-path.spec.ts`
- Current result: 1 passed
