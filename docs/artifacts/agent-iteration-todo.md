# Agent Iteration TODO (Post-MVP Expansion)

Date: 2026-05-14
Source prompts folder: .github/prompts
Approach: complete one agent at a time, pause for review, then continue.

## Steps

- [x] 1. buildathon-kickoff.prompt.md
- [x] 2. buildathon-po-ba-agent.prompt.md
- [x] 3. buildathon-developer-platform-agent.prompt.md
- [x] 4. buildathon-qa-ste-agent.prompt.md
- [x] 5. buildathon-security-verifier-agent.prompt.md
- [x] 6. buildathon-support-triage-agent.prompt.md
- [ ] 7. buildathon-bugbot-agent.prompt.md
- [ ] 8. expert-software-reviewer.prompt.md

## Pause Rule

After each step:
1. Save the artifact for that agent under `docs/artifacts/`.
2. Mark that step complete here.
3. Pause and request your review before continuing.

## Step 4 Evidence (2026-05-14)

- Artifact updated: docs/artifacts/qa-ste-minimum-test-plan.md
- API evidence: 15 passed (`python3 -m pytest code/tests/api -q --cov=code/backend --cov-report=xml:code/tests/api/coverage.xml`)
- Coverage evidence: 86% backend module coverage
- E2E evidence: 1 passed (`npm test` in `code/tests/e2e`)

## Step 5 Evidence (2026-05-14)

- Artifact updated: docs/artifacts/security-verifier-review.md
- Hardening implemented: employee ID format validation, leave/schedule date-time validation, bounded correction reason length
- Security tests added: code/tests/api/test_security_hardening.py
- API evidence: 20 passed (`python3 -m pytest code/tests/api -q --cov=code/backend --cov-report=xml:code/tests/api/coverage.xml`)
- Coverage evidence: 95% backend module coverage

## Step 6 Evidence (2026-05-14)

- Artifact updated: docs/artifacts/support-triage-plan.md
- Added triage pathways for leave, scheduling, payroll/compliance, and diagnostics drift
- Added operator command set for fastest endpoint-based incident narrowing
