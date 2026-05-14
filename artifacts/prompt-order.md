# Prompt Order and Activities

This file tracks the execution order for BuildAThon prompts and the activities tied to each prompt.

## Run Order

| Step | Prompt / Activity | Purpose | Expected Output | Status |
|---|---|---|---|---|
| 1 | Kickoff prompt: .github/prompts/buildathon-kickoff.prompt.md | Align scope to 4-hour MVP and avoid full-platform drift | MVP summary, deferred scope, smallest next decision | Completed |
| 2 | PO/BA prompt: .github/prompts/buildathon-po-ba-agent.prompt.md | Define the minimum stories, acceptance criteria, validation, and deferrals | Small story set, concrete criteria, explicit out-of-scope | Completed |
| 3 | Developer prompt: .github/prompts/buildathon-developer-platform-agent.prompt.md | Plan thin contract-first implementation path | Minimum entities, FastAPI surface, React surface, build order | Pending |
| 4 | QA/STE prompt: .github/prompts/buildathon-qa-ste-agent.prompt.md | Define minimum evidence to prove MVP behavior | API tests + one Playwright flow test | Pending |
| 5 | Security prompt: .github/prompts/buildathon-security-verifier-agent.prompt.md | Perform practical MVP security sanity pass | Input validation checks, safe errors, secret handling checks | Pending |
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

## Update Rules

- Update status after each prompt run.
- Keep scope locked to MVP unless an explicit decision expands it.
- Do not mark a step completed without a concrete artifact or test evidence.
