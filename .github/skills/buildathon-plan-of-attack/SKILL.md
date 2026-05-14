---
name: buildathon-plan-of-attack
description: 'Plan and orchestrate the BBSI BuildAThon Workforce Time Tracking and Payroll Integration Platform. Use when breaking the project into child skills for requirements, architecture, API, database, UI, QA, security, platform, support, and BugBot delivery.'
argument-hint: 'Optional scope such as MVP first, full platform, or a specific workstream'
user-invocable: true
---

# BuildAThon Plan Of Attack

Use this skill before implementation. It converts the three repo documents into a phased delivery plan and a set of smaller skills that can be implemented independently without losing traceability or governance.

If the BuildAThon is time-boxed to roughly four hours, do not use this skill by itself as the execution target.
Read this skill for the big picture, then switch immediately to `../buildathon-mvp-4-hour/SKILL.md` and treat that MVP skill as the primary execution mode.

## Source Documents

Base this plan on all three project documents:

- `bbsi_buildathon_2026_requirements_only.md`
- `Bbsi Buildathon 2026 Ade Guide.pdf`
- `BuildAThon Operation Model.docx`

Treat conflicts or ambiguities using this priority order:

1. Functional and technical requirements from the markdown file
2. Agent role and ADE expectations from the PDF
3. Delivery sequencing, gates, and artifact expectations from the DOCX

## Chosen Stack

For this project, use these implementation defaults unless the starter repo forces a different path:

- Backend API: FastAPI
- Frontend UI: React
- End-to-end UI tests: Playwright with TypeScript

Treat these as committed choices for planning, prompting, and implementation.

## Non-Negotiable Rules

- Do not start implementation before requirements decomposition, architecture framing, and traceability setup exist.
- Keep the work API-first. UI, tests, and integrations should align to explicit contracts.
- Use FastAPI for backend API work, React for frontend work, and Playwright with TypeScript for end-to-end UI testing.
- Require human approval gates after planning, architecture, schema/API design, QA evidence, and security review.
- Build for future extensibility, but do not spend BuildAThon time implementing optional future integrations such as CIAM or event-driven architecture.
- Treat QA, security, platform, support, and BugBot workflows as part of the product, not cleanup work.
- Work in thin vertical slices, but keep ownership separated by skill so agents can collaborate predictably.

## Preferred 4-Hour Mode

When time is severely constrained, use `../buildathon-mvp-4-hour/SKILL.md` as the execution overlay.

That MVP skill is the preferred entry point for a four-hour BuildAThon because it narrows scope to a credible time-capture slice, defines explicit deferrals, and keeps the demo target realistic.

In 4-hour mode:

1. Read this plan skill for structure and context.
2. Switch to the MVP skill as the operational source of truth.
3. Use the role prompts only to move the MVP forward.
4. Do not expand back toward the full platform unless the MVP is stable.

## What Success Looks Like

The project should deliver:

- A working Workforce Time Tracking and Payroll Integration Platform
- A clean API-first backend with database support
- A usable web UI with responsive behavior for mobile workflows
- Automated UI and API tests with evidence
- Security validation and secure coding checks
- Platform automation, observability, and deployment readiness
- Operational triage and BugBot-style defect recreation support
- Traceable evidence from requirement to implementation to validation

## Mandatory Planning Artifacts

Create these documents before feature implementation accelerates:

1. `planning-framework.md`
2. `roadmap.md`
3. `QUICK-REFERENCE.md`
4. `requirements-traceability-matrix.md`
5. `user-story-template.md`

These artifacts are the shared contract for every child skill.

## Recommended Delivery Sequence

Follow this order. Later skills can overlap only after the dependency gate is satisfied.

1. Requirements decomposition
2. Architecture and roadmap
3. Data model and API contracts
4. Backend implementation
5. Frontend workflows
6. QA automation
7. Security verification
8. Platform delivery
9. Support triage
10. BugBot remediation

## Functional Slices

Plan implementation around these slices. Child skills should work one slice at a time whenever possible.

1. Core time capture
   Employee clock-in/out, punch validation, duplicate prevention, attendance tracking, missing punch detection
2. Corrections and approvals
   Time correction workflow, manager review, audit logging, attendance exceptions
3. Leave and scheduling
   Leave requests, approvals, balances, shift scheduling, break enforcement, core-hour validation
4. Payroll readiness
   Timesheets, overtime, holiday rules, night differential, PTO, comp time, payroll export
5. Compliance and reporting
   Labor-rule validation, tax/compliance reporting, audit trails, operational and CrossCheck reporting
6. Enterprise readiness
   Multi-company, multi-location, policy configuration, role-based access control, responsive/mobile support

## Child Skill Breakdown

Create the following child skills under `.github/skills/`. Each skill should have a specific description, a clear handoff contract, and explicit done criteria.

### 1. requirements-decomposition

Use when turning BuildAThon requirements into epics, stories, workflows, validations, and acceptance criteria.

Inputs:

- The three source documents
- Any business constraints from the team

Outputs:

- Capability map by actor
- Epics and user stories
- Acceptance criteria with positive, negative, and edge cases
- Initial traceability matrix rows
- MVP vs later-phase scope split

Done when:

- Every functional requirement has at least one mapped story
- Each story has acceptance criteria and business rules
- MVP scope is explicit

### 2. architecture-and-roadmap

Use when defining solution boundaries, delivery phases, module ownership, and high-level technical design.

Inputs:

- Requirements decomposition outputs

Outputs:

- Architecture diagram and component boundaries
- Delivery roadmap with dependencies
- Environment assumptions
- Approval checkpoints
- Integration posture for future extensibility

Done when:

- The team can explain what belongs in frontend, backend, database, integrations, and operations
- A phased roadmap exists and is realistic for BuildAThon time limits

### 3. data-and-api-contracts

Use when defining the domain model, database schema, API contracts, validation rules, and audit needs.

Inputs:

- Approved stories and architecture

Outputs:

- Entity model and schema proposal
- OpenAPI or equivalent endpoint contract definitions
- Request and response shapes
- Validation rules and error cases
- Audit and reporting data requirements

Done when:

- UI and backend agents can work from explicit contracts
- Core entities cover time, leave, payroll, audit, reporting, and access control needs

### 4. backend-implementation

Use when implementing services, repositories, endpoints, integrations, and business rules behind the approved contracts.

Inputs:

- Data model and API contracts

Outputs:

- Backend endpoints and service logic
- Persistence layer
- Business rule enforcement
- Seed or synthetic data support
- Error handling and logging hooks

Done when:

- Core API flows work for the current slice
- Logging and validation are present
- Contract mismatches are resolved before UI integration expands

### 5. frontend-workflows

Use when building the web UI, responsive workflows, data entry, approvals, reporting views, and error states.

Inputs:

- Approved contracts
- Story-level workflow expectations

Outputs:

- Time capture UI
- Timesheet and correction flows
- Leave and scheduling flows
- Reporting and admin views
- Responsive/mobile-friendly behavior
- Accessible forms and feedback states

Done when:

- Each implemented UI flow maps to a story and API contract
- Failure and validation states are visible and testable

### 6. qa-automation

Use when generating test plans, API tests, UI tests, synthetic data, and evidence tied to acceptance criteria.

Inputs:

- Stories, contracts, and implemented flows

Outputs:

- Test plan per functional slice
- API automation coverage
- UI automation coverage
- Negative and boundary tests
- Evidence for traceability matrix

Done when:

- Happy path, negative path, and boundary coverage exist for the active slice
- Evidence can be shown in the demo

### 7. security-verification

Use when validating authentication, authorization, secrets handling, dependency posture, and API security.

Inputs:

- Running application and repository configuration

Outputs:

- Security checklist and findings
- Dependency scan results
- Secret exposure review
- RBAC and API validation review
- Required remediation items

Done when:

- Critical issues are fixed or explicitly accepted
- Security evidence is demo-ready

### 8. platform-delivery

Use when setting up Codespaces, developer bootstrap, CI or workflow automation, deployment path, and observability.

Inputs:

- Architecture and implementation decisions

Outputs:

- Reproducible dev environment
- Build and test workflows
- Deployment steps or automation
- Logging, tracing, or metrics hooks
- Quick-start guidance for judges or teammates

Done when:

- A new teammate can get running quickly
- The platform can show credible automation and operational readiness

### 9. support-triage

Use when defining operational diagnostics, issue classification, and root-cause workflows for production-like incidents.

Inputs:

- Logging and runtime behavior

Outputs:

- Triage playbooks
- Incident categories and severity model
- Log correlation guidance
- Root-cause analysis workflow

Done when:

- The team can demonstrate how an issue would be diagnosed in production

### 10. bugbot-remediation

Use when recreating failures, isolating the probable cause, and suggesting or implementing targeted fixes.

Inputs:

- A concrete defect report or failing behavior

Outputs:

- Reproduction steps
- Root-cause hypothesis
- Proposed fix plan
- Optional remediation pull request or patch

Done when:

- The defect is reproducible or the uncertainty is narrowed to a small set of causes
- The fix is validated against the failing behavior

## Handoff Contracts Between Skills

Each child skill must leave behind artifacts that the next skill can consume without re-discovery.

- Requirements to architecture: epics, stories, acceptance criteria, actors, and business rules
- Architecture to data/API: bounded modules, slice order, integration boundaries, and approval notes
- Data/API to backend and frontend: schema, contract definitions, error model, validation rules, and example payloads
- Implementation to QA: working flows, seeded test data, and traceable acceptance criteria IDs
- QA to security and platform: test evidence, known gaps, environment assumptions, and exposed surfaces
- Security and platform to support/BugBot: logs, failure modes, deployment context, and remediation history

## Execution Guardrails

- Prefer implementing one functional slice across requirements, API, UI, QA, and security instead of finishing one discipline for the whole system.
- Keep the first slice small: core time capture plus audit logging is the best anchor.
- Treat payroll calculations and reporting as later slices unless the team is ahead of schedule.
- Do not let UI work outrun API contracts.
- Do not let backend work outrun story-level validation rules.
- Do not call the platform complete without a reproducible setup path and visible observability hooks.

## Suggested MVP For BuildAThon Time Constraints

If time is tight, prioritize this order:

1. Core time capture with clock-in, clock-out, punch validation, and audit logging
2. Timesheet review and correction workflow
3. Basic leave request and approval flow
4. Payroll export readiness with at least one calculation path
5. One compliance or reporting view
6. QA evidence, security review, platform automation, and one operational incident walkthrough

## How To Use This Skill

1. Read the three source documents.
2. If the session is time-boxed, read `../buildathon-mvp-4-hour/SKILL.md` and adopt it as the primary execution target.
3. Create or update the planning artifacts that are justified for the available time.
4. Pick the current functional slice.
5. Create the minimum child skills needed for that slice, or use targeted role prompts if that is faster.
6. Implement, test, secure, and operationalize the slice without widening scope unnecessarily.
7. Update traceability and roadmap before moving to the next slice.

## Good Starting Point

Yes. A plan-of-attack skill is the right starting point for this BuildAThon.

It gives the agent a stable orchestration layer, keeps the team from jumping straight into code, and creates a clean way to break work into focused child skills such as API, UI, QA, security, platform, support, and BugBot.