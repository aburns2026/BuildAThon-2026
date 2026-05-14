# Prompt Order and Activities

This file tracks the execution order for BuildAThon prompts and the activities tied to each prompt.

## Run Order

| Step | Prompt / Activity | Purpose | Expected Output | Status |
|---|---|---|---|---|
| 1 | Kickoff prompt: .github/prompts/buildathon-kickoff.prompt.md | Align scope to 4-hour MVP and avoid full-platform drift | MVP summary, deferred scope, smallest next decision | Completed |
| 2 | PO/BA prompt: .github/prompts/buildathon-po-ba-agent.prompt.md | Define the minimum stories, acceptance criteria, validation, and deferrals | Small story set, concrete criteria, explicit out-of-scope | Completed |
| 2.5 | MVP lock checkpoint: artifacts/mvp-lock.md | Freeze scope before implementation and prevent expansion drift | Locked in-scope list, deferred list, guardrails, next decision | Completed |
| 3 | Developer prompt: .github/prompts/buildathon-developer-platform-agent.prompt.md | Plan thin contract-first implementation path | Minimum entities, FastAPI surface, React surface, build order | Completed |
| 4 | QA/STE prompt: .github/prompts/buildathon-qa-ste-agent.prompt.md | Define minimum evidence to prove MVP behavior | API tests + one Playwright flow test | Completed |
| 5 | Security prompt: .github/prompts/buildathon-security-verifier-agent.prompt.md | Perform practical MVP security sanity pass | Input validation checks, safe errors, secret handling checks | Completed |
| 6 | Optional support prompt: .github/prompts/buildathon-support-triage-agent.prompt.md | Add operational triage flow if time remains | Triage process and support notes | Optional |
| 7 | Optional BugBot prompt: .github/prompts/buildathon-bugbot-agent.prompt.md | Structured defect reproduction/remediation flow if needed | Bug report and fix workflow notes | Optional |

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

- stories: artifacts/mvp-stories.md
- acceptance criteria: artifacts/mvp-acceptance-criteria.md
- validation rules: artifacts/mvp-validation-rules.md
- deferred scope: artifacts/mvp-deferred-scope.md
- mvp lock decision: artifacts/mvp-lock.md
- developer contract-first plan: artifacts/developer-contract-first-plan.md
- qa/ste minimum test plan: artifacts/qa-ste-minimum-test-plan.md
- security verifier review: artifacts/security-verifier-review.md
- playwright main-path test: code/tests/e2e/specs/mvp-main-path.spec.ts
- demo-ready checklist: artifacts/demo-ready-checklist.md

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
- Artifacts or evidence: artifacts/developer-contract-first-plan.md
- Notes/blockers: Plan constrained to artifacts/mvp-lock.md; no scope expansion.

- Date: 2026-05-14
- Step: 4 QA/STE prompt
- Status change: Pending -> Completed
- Artifacts or evidence: artifacts/qa-ste-minimum-test-plan.md
- Notes/blockers: Minimum API tests plus one Playwright main-path test defined; scope constrained to artifacts/mvp-lock.md.

- Date: 2026-05-14
- Step: 5 Security prompt
- Status change: Pending -> Completed
- Artifacts or evidence: artifacts/security-verifier-review.md
- Notes/blockers: Practical findings separated into must-fix vs deferred; remained within MVP scope boundary.

- Date: 2026-05-14
- Step: 4 QA/STE evidence update
- Status change: Completed -> Completed (evidence added)
- Artifacts or evidence: code/tests/e2e/specs/mvp-main-path.spec.ts
- Notes/blockers: Added required Playwright main-path flow including duplicate validation visibility.

- Date: 2026-05-14
- Step: 10 Demo checklist handoff
- Status change: Started
- Artifacts or evidence: artifacts/demo-ready-checklist.md
- Notes/blockers: Checklist created for final pre-demo gate and evidence walkthrough.
