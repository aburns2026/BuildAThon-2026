# How To Get Started

This is the practical starting flow for the BuildAThon after you open the sample GitHub Codespace.

Do not treat this as a full product build.
Treat it as a 4-hour sprint to produce one credible MVP slice that maps to the challenge.

## What To Treat As Source Of Truth

Use the repo documents in this order:

1. `bbsi_buildathon_2026_requirements_only.md`
   This is the real scope document. Use it for what the application is supposed to demonstrate.
2. `Bbsi Buildathon 2026 Ade Guide.pdf`
   Use this for ADE framing, judging language, and how to talk about AI-assisted delivery.
3. `BuildAThon Operation Model.docx`
   Treat this as optional background. Do not let it expand the scope.

Use the repo workflow assets in this order:

1. `.github/skills/buildathon-plan-of-attack/SKILL.md`
   Big-picture operating model.
2. `.github/skills/buildathon-mvp-4-hour/SKILL.md`
   Actual execution target for tomorrow.
3. `.github/prompts/buildathon-kickoff.prompt.md`
   Best entry point for a new chat session.

## Fixed Technology Choices

Use these defaults for tomorrow unless the starter repo makes one of them impossible:

- API: FastAPI
- UI: React
- E2E UI tests: Playwright with TypeScript

Do not spend time re-deciding the stack in the room.

## The Only Sane Goal

The real target is not the full Workforce Time Tracking and Payroll Integration Platform.

The sane target is the 4-hour MVP:

- employee clock-in
- employee clock-out
- punch validation
- duplicate punch prevention
- shift history or today summary
- audit log entries
- payroll-ready summary or export endpoint
- a few tests

Everything else is deferred unless the MVP is stable and time remains.

## Flow After Opening The Sample Codespace

### 1. Verify the starter repo and do not improvise scope

- Open the starter repository in Codespaces.
- Confirm the starter repo can support FastAPI for the backend, React for the UI, and Playwright with TypeScript for e2e UI tests.
- Figure out the database choice and how to run the app and tests.
- Do not start coding yet.
- Do not assume the starter repo wants the whole challenge implemented.

Your first job is to confirm what the sample repo already gives you.

### 2. Open Copilot Chat and start with the kickoff prompt

- In chat, run `.github/prompts/buildathon-kickoff.prompt.md`.
- Let it read the requirements document, the ADE guide, the main plan skill, and the MVP skill.
- Ask it to summarize the repo in terms of the 4-hour MVP, not the full challenge.

Expected outcome:

- a short summary of what you are building now
- what is deferred
- the smallest next decision

### 3. Lock the MVP before implementation

- Do not let the session wander into leave management, scheduling, full payroll rules, or enterprise architecture debates.
- Use `.github/skills/buildathon-mvp-4-hour/SKILL.md` as the scope boundary.
- If the agent tries to widen scope, redirect it back to the MVP.

The MVP is the entry point. The full plan is only context.

### 4. Run the PO BA prompt first

- Run `.github/prompts/buildathon-po-ba-agent.prompt.md`.
- Ask it for the minimum stories, acceptance criteria, validation rules, and explicit deferred scope for the MVP.

Expected outcome:

- a short MVP summary
- a tiny set of stories
- concrete acceptance criteria
- clear out-of-scope items

Do not overproduce documents. The point is to lock the build target.

### 5. Run the developer prompt next

- Run `.github/prompts/buildathon-developer-platform-agent.prompt.md`.
- Ask it to plan the thinnest contract-first implementation path against the actual starter repo.

Expected outcome:

- minimum entities
- minimum FastAPI API surface
- minimum React UI surface
- build order for the slice

This is where you start implementation.

### 6. Build the vertical slice in this order

1. Define the core entities
   Employee, Punch, Shift, AuditEvent
2. Define the minimum endpoints
   Clock-in, clock-out, shifts or summary, audit history, payroll summary
3. Implement backend logic first
   Validation, duplicate prevention, audit logging, persistence
4. Add the thin UI
   Clock-in, clock-out, status, history or summary
5. Make the demo flow work end to end

Do not build admin features, leave flows, or rich reporting until the main demo flow works.

### 7. Add the smallest useful test set

- Run `.github/prompts/buildathon-qa-ste-agent.prompt.md`.
- Ask for the minimum API and UI tests needed to prove the MVP.

At minimum, get:

- successful clock-in
- duplicate or invalid punch rejected
- successful clock-out
- one Playwright TypeScript UI flow test for the main path

### 8. Do a lightweight security pass

- Run `.github/prompts/buildathon-security-verifier-agent.prompt.md`.
- Ask for the shortest practical review of the current MVP.

Focus on:

- input validation
- safe error handling
- secrets exposure
- obvious API misuse risks

This is a final cleanup pass, not a reason to redesign the app.

### 9. Only use support and BugBot prompts if needed

These are optional unless:

- the judges care a lot about operational support
- you hit a defect and need a structured triage flow
- you have extra time

Optional prompts:

- `.github/prompts/buildathon-support-triage-agent.prompt.md`
- `.github/prompts/buildathon-bugbot-agent.prompt.md`

### 10. Finish with a demo-ready checklist

Before time runs out, confirm:

- the app starts reliably
- the main flow works live
- an invalid punch case is visible
- audit logging is visible
- payroll summary or export is visible
- tests can be shown
- deferred scope is explicit and honest

## Recommended Time Split

### First 30 minutes

- inspect starter repo
- run kickoff prompt
- lock MVP
- get PO BA output
- get developer plan

### Next 90 minutes

- implement backend core flow
- add validation
- add audit logging
- add persistence

### Next 60 minutes

- build thin UI
- connect UI to API
- verify the end-to-end flow

### Final 60 minutes

- add minimal tests
- fix demo blockers
- do security sanity pass
- write short notes for architecture and deferred scope

## What Not To Do

- Do not try to cover every requirement bullet.
- Do not build every agent role as a runtime service.
- Do not let the word document bully you into fake process overhead.
- Do not spend an hour on architecture diagrams before the main flow works.
- Do not chase enterprise completeness.
- Do not widen scope after implementation starts unless the MVP is already solid.

## If You Get Stuck

If the starter repo is confusing, go back to this sequence:

1. kickoff prompt
2. PO BA prompt
3. developer prompt
4. QA prompt
5. security prompt

That is the default path.

## Bottom Line

Tomorrow is not about building the whole platform.

It is about building one stable, believable slice that clearly maps to the requirements document and can be explained using the ADE guide language.