# Prompt Order and Activities

This file tracks the execution order for BuildAThon prompts and the activities tied to each prompt.

## Run Order

| Step | Prompt / Activity | Purpose | Expected Output | Status |
|---|---|---|---|---|
| 1 | Kickoff prompt: .github/prompts/buildathon-kickoff.prompt.md | Align scope to 4-hour MVP and avoid full-platform drift | MVP summary, deferred scope, smallest next decision | Completed |
| 2 | PO/BA prompt: .github/prompts/buildathon-po-ba-agent.prompt.md | Define the minimum stories, acceptance criteria, validation, and deferrals | Small story set, concrete criteria, explicit out-of-scope | Completed |
| 2.5 | MVP lock checkpoint: docs/artifacts/scope-lock.md | Freeze scope before implementation and prevent expansion drift | Locked in-scope list, deferred list, guardrails, next decision | Completed |
| 3 | Developer prompt: .github/prompts/buildathon-developer-platform-agent.prompt.md | Plan thin contract-first implementation path | Minimum entities, FastAPI surface, React surface, build order | Completed |
| 4 | QA/STE prompt: .github/prompts/buildathon-qa-ste-agent.prompt.md | Define minimum evidence to prove MVP behavior | API tests + one Playwright flow test | Completed |
| 5 | Security prompt: .github/prompts/buildathon-security-verifier-agent.prompt.md | Perform practical MVP security sanity pass | Input validation checks, safe errors, secret handling checks | Completed |
| 6 | Optional support prompt: .github/prompts/buildathon-support-triage-agent.prompt.md | Add operational triage flow if time remains | Triage process and support notes | Completed |
| 7 | Optional BugBot prompt: .github/prompts/buildathon-bugbot-agent.prompt.md | Structured defect reproduction/remediation flow if needed | Bug report and fix workflow notes | Completed |

## Activities by Step

### 1. Kickoff
- Read requirements and source docs.
- Lock to the 4-hour MVP scope boundary.
- Confirm deferred features are explicit.

### 2. PO/BA
- Finalize MVP stories.
- Finalize acceptance criteria.
- Finalize validation rules.
- Finalize deferred scope list.

### 3. Developer
- Define entities: Employee, Punch, Shift, AuditEvent.
- Define endpoints: clock-in, clock-out, shifts/summary, audit, payroll summary.
- Implement backend validation, duplicate prevention, and audit logging.
- Add thin UI flow for clock-in/out and status/history.

### 4. QA/STE
- Add API tests for successful clock-in, duplicate/invalid rejection, and successful clock-out.
- Add one Playwright UI main-path test.

### 5. Security
- Check input validation and safe error handling.
- Check for secrets exposure.
- Check obvious API misuse risks.

### 6. Optional Support
- Add support and triage notes only if MVP is stable.

### 7. Optional BugBot
- Add defect workflow only if time remains after demo readiness.

## Current Artifacts Produced

- stories: docs/artifacts/product-stories.md
- acceptance criteria: docs/artifacts/acceptance-criteria.md
- validation rules: docs/artifacts/validation-rules.md
- deferred scope: docs/artifacts/deferred-scope.md
- mvp lock decision: docs/artifacts/scope-lock.md
- developer contract-first plan: docs/artifacts/developer-contract-first-plan.md
- qa/ste minimum test plan: docs/artifacts/qa-ste-minimum-test-plan.md
- security verifier review: docs/artifacts/security-verifier-review.md
- playwright main-path test: code/tests/e2e/specs/main-path.spec.ts
- demo-ready checklist: docs/artifacts/demo-ready-checklist.md
- support triage plan: docs/artifacts/support-triage-plan.md
- bugbot defect report: docs/artifacts/bugbot-defect-report.md
- frontend unit tests: code/frontend/src/App.test.tsx
- enterprise/reporting UI coverage: code/tests/e2e/specs/admin-reporting.spec.ts

## Update Rules

- Update status after each prompt run.
- Keep scope locked to MVP unless an explicit decision expands it.
- Do not mark a step completed without a concrete artifact or test evidence.

## Hard Rule: Tracker Is Source Of Truth

- After every prompt step, update this file immediately before starting the next step.
- Each completed step must include both a status change and an artifact or evidence reference.
- If a step is blocked, set status to Blocked and record the blocker and next action.
- No implementation step starts unless the prior step status is current in this file.

## Activity Log (Append Only)

Use this log after each step:

- Date:
- Step:
- Status change:
- Artifacts or evidence:
- Notes/blockers:

- Date: 2026-05-14
- Step: 3 Developer prompt
- Status change: Pending -> Completed
- Artifacts or evidence: docs/artifacts/developer-contract-first-plan.md
- Notes/blockers: Plan constrained to docs/artifacts/scope-lock.md; no scope expansion.

- Date: 2026-05-14
- Step: 4 QA/STE prompt
- Status change: Pending -> Completed
- Artifacts or evidence: docs/artifacts/qa-ste-minimum-test-plan.md
- Notes/blockers: Minimum API tests plus one Playwright main-path test defined; scope constrained to docs/artifacts/scope-lock.md.

- Date: 2026-05-14
- Step: 5 Security prompt
- Status change: Pending -> Completed
- Artifacts or evidence: docs/artifacts/security-verifier-review.md
- Notes/blockers: Practical findings separated into must-fix vs deferred; remained within MVP scope boundary.

- Date: 2026-05-14
- Step: 4 QA/STE evidence update
- Status change: Completed -> Completed (evidence added)
- Artifacts or evidence: code/tests/e2e/specs/main-path.spec.ts
- Notes/blockers: Added required Playwright main-path flow including duplicate validation visibility.

- Date: 2026-05-14
- Step: 10 Demo checklist handoff
- Status change: Started
- Artifacts or evidence: docs/artifacts/demo-ready-checklist.md
- Notes/blockers: Checklist created for final pre-demo gate and evidence walkthrough.

- Date: 2026-05-14
- Step: 10 Demo checklist execution
- Status change: Started -> Completed
- Artifacts or evidence: docs/artifacts/demo-ready-checklist.md, code/tests/e2e/specs/main-path.spec.ts
- Notes/blockers: Evidence runs completed (API: 7 passed, Playwright: 1 passed on retry) and checklist items marked complete.

- Date: 2026-05-14
- Step: 6 Optional Support prompt
- Status change: Optional -> Completed
- Artifacts or evidence: docs/artifacts/support-triage-plan.md
- Notes/blockers: Added minimum incident triage path and diagnostics for demo operations.

- Date: 2026-05-14
- Step: 7 Optional BugBot prompt
- Status change: Optional -> Completed
- Artifacts or evidence: docs/artifacts/bugbot-defect-report.md, code/tests/e2e/specs/main-path.spec.ts
- Notes/blockers: Documented E2E strict-mode selector defect, smallest fix, and verification evidence.

- Date: 2026-05-14
- Step: 4 QA/STE prompt (post-MVP expansion)
- Status change: Completed -> Completed (expansion evidence refreshed)
- Artifacts or evidence: docs/artifacts/qa-ste-minimum-test-plan.md, code/tests/api/test_expansion_contracts.py, code/tests/api/coverage.xml
- Notes/blockers: Added and validated API evidence for leave/scheduling/corrections/compliance/enterprise baseline; API 15 passed, E2E 1 passed, backend coverage 86%.

- Date: 2026-05-14
- Step: 5 Security prompt (post-MVP expansion)
- Status change: Completed -> Completed (security evidence refreshed)
- Artifacts or evidence: docs/artifacts/security-verifier-review.md, code/tests/api/test_security_hardening.py, code/tests/api/coverage.xml
- Notes/blockers: Added practical validation hardening for ID/date/datetime/text boundaries and verified with API tests (20 passed, backend coverage 95%).

- Date: 2026-05-14
- Step: 6 Optional Support prompt (post-MVP expansion)
- Status change: Completed -> Completed (support runbook refreshed)
- Artifacts or evidence: docs/artifacts/support-triage-plan.md, code/backend/main.py
- Notes/blockers: Expanded triage flow to include leave/scheduling/payroll/compliance/ops diagnostics contracts and added quick operator endpoint checks.

- Date: 2026-05-14
- Step: 3 Developer prompt (post-MVP expansion - RBAC enforcement)
- Status change: Completed -> Completed (endpoint authorization expanded)
- Artifacts or evidence: code/backend/main.py, code/tests/api/test_phase2_contracts.py, code/tests/api/test_expansion_contracts.py
- Notes/blockers: Added endpoint-level `X-Role` authorization checks on protected routes (leave approval, scheduling, policy updates, payroll export/integration, reports, balance adjustments); API tests passing (27 passed).

- Date: 2026-05-15
- Step: 4 QA/STE prompt (post-review hardening refresh)
- Status change: Completed -> Completed (test hardening expanded)
- Artifacts or evidence: code/tests/e2e/playwright.config.ts, code/tests/e2e/specs/support.ts, code/tests/e2e/specs/negative-paths.spec.ts, code/tests/e2e/specs/admin-reporting.spec.ts, code/tests/api/test_repository_logic.py, code/tests/api/test_compose_smoke.py
- Notes/blockers: Added isolated Playwright reset support, stronger E2E assertions, negative-path browser coverage, direct repository logic tests, and a gated compose smoke test; evidence now API 42 passed, Playwright 12 passed, frontend unit 3 passed.

- Date: 2026-05-15
- Step: 3 Developer prompt (post-review UI expansion)
- Status change: Completed -> Completed (frontend coverage expanded)
- Artifacts or evidence: code/frontend/src/App.tsx, code/frontend/src/App.test.tsx, code/frontend/README.md, docs/artifacts/planning-framework.md, docs/artifacts/roadmap.md
- Notes/blockers: Added enterprise admin directory/location views plus operational, crosscheck, and payroll export summaries in the React UI, and established a small Vitest/Testing Library baseline for frontend correctness.

- Date: 2026-05-15
- Step: 3 Developer prompt (simple enterprise admin hardening)
- Status change: Completed -> Completed (editable admin workflows added)
- Artifacts or evidence: code/backend/main.py, code/backend/models.py, code/frontend/src/App.tsx, code/tests/api/test_phase2_contracts.py, code/tests/e2e/specs/admin-reporting.spec.ts
- Notes/blockers: Added editable policy and employee-location management in the UI, plus stubbed downstream notification and secret-provider configuration surfaces. Final validation: API 43 passed, Playwright 12 passed, frontend unit 3 passed. Real downstream delivery and real secret backends still remain out of scope.
