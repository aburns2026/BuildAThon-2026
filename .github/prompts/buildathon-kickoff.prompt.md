---
name: "BuildAThon Kickoff"
description: "Prime a new BuildAThon session by reviewing the source docs, the main plan skill, and the 4-hour MVP skill, then focus execution on the MVP."
argument-hint: "Optional note such as solo mode or MVP first"
agent: "agent"
---

You are helping build a BBSI BuildAThon project: a Workforce Time Tracking & Payroll Integration Platform.

Before doing implementation work, orient yourself to the project materials, read the main orchestrator skill for context, and then use the MVP skill as the primary execution target.

Project context:

- This repository is for a BuildAThon entry focused on AI-assisted enterprise software delivery.
- The goal is not to jump straight into code. The goal is to work in a controlled sequence: requirements, architecture, contracts, implementation, QA, security, platform, support, and BugBot-style remediation.
- We want disciplined decomposition, traceability, API-first design, human approval gates, and a realistic MVP-first plan.
- Use FastAPI for the API, React for the UI, and Playwright with TypeScript for end-to-end UI tests.

Primary source documents to read first:

- [bbsi_buildathon_2026_requirements_only.md](../../bbsi_buildathon_2026_requirements_only.md)
- [Bbsi Buildathon 2026 Ade Guide.pdf](../../Bbsi%20Buildathon%202026%20Ade%20Guide.pdf)
- [BuildAThon Operation Model.docx](../../BuildAThon%20Operation%20Model.docx)

Skills to read first:

- [buildathon-plan-of-attack](../skills/buildathon-plan-of-attack/SKILL.md)
- [buildathon-mvp-4-hour](../skills/buildathon-mvp-4-hour/SKILL.md)

How to interpret those skills:

- `buildathon-plan-of-attack` is the big-picture operating model.
- `buildathon-mvp-4-hour` is the preferred 4-hour execution mode and should be the focal point for implementation decisions.

What those skills already define:

- The recommended delivery sequence
- The functional slices
- The child skills to create later
- The planning artifacts expected before implementation accelerates
- Handoff contracts between requirements, architecture, API, backend, frontend, QA, security, platform, support, and BugBot workflows
- The specific 4-hour MVP target, explicit deferrals, minimum evidence, and demo narrative

How to approach this session:

1. Read the three source documents.
2. Read [buildathon-plan-of-attack](../skills/buildathon-plan-of-attack/SKILL.md).
3. Read [buildathon-mvp-4-hour](../skills/buildathon-mvp-4-hour/SKILL.md).
4. Treat the MVP skill as the primary execution target unless the user explicitly asks for broader planning.
5. Summarize the project in practical terms: what we are building now, what is deferred, and the main engineering constraints.
6. Do not generate all child skills immediately unless explicitly asked.
7. Do not jump straight into implementation unless explicitly asked.
8. Use the main orchestrator skill for context and sequencing, but use the MVP skill as the source of truth for near-term scope.
9. When proposing next steps, keep them small, ordered, and realistic for a four-hour window.

Important framing:

- The best first conversation is about scope, MVP, skill boundaries, and artifact strategy.
- The first implementation slice is the MVP time-capture flow described in the MVP skill, unless the user redirects.
- UI should not outrun API contracts.
- Backend should not outrun accepted stories and validation rules.
- QA, security, platform, support, and BugBot are part of the product story, not afterthoughts.
- Honest deferral is better than fake completeness.

When you respond after reading the materials:

- Start with a short summary of the project and the recommended BuildAThon approach.
- Then propose the smallest sensible next decision for the user to make within the MVP.
- Keep the response concise, concrete, and execution-oriented.