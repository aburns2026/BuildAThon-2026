---
name: buildathon-current-state-reconciliation
description: 'Assess source-of-truth requirements, inspect docs/artifacts, code, and tests, then reconcile stale markdown and implementation gaps with the current repository state.'
argument-hint: 'Optional focus such as docs only, role-specific artifact, or implementation gap'
user-invocable: true
---

# BuildAThon Current-State Reconciliation

Use this skill when the repository already has implementation and the main problem is drift between:

- source-of-truth requirements
- docs/artifacts markdown files
- actual backend, frontend, and test coverage

This skill is the default operating mode for maintenance and repo-refresh work.

## Source Priority

Use these sources in this order:

1. `../../docs/bbsi_buildathon_2026_requirements_only.md`
2. `../../docs/Bbsi Buildathon 2026 Ade Guide.pdf`
3. current code and tests under `../../code/`
4. living project docs under `../../docs/artifacts/`

If docs/artifacts disagree with source requirements or code, update them.
If code is missing and the active task requires the docs to be true, implement the smallest needed change.

## What This Skill Does

1. Scan `docs/artifacts/` for stale, incomplete, or contradictory markdown.
2. Compare the artifact claims against the source-of-truth files.
3. Compare the artifact claims against backend routes, frontend behavior, and test evidence.
4. Decide whether the needed action is:
   - markdown refresh only
   - markdown plus tests
   - markdown plus implementation
5. Update all related artifacts needed for consistency, not just one file.

## Default Artifact Targets

Common files to inspect and update when they are affected:

- `planning-framework.md`
- `product-stories.md`
- `acceptance-criteria.md`
- `validation-rules.md`
- `requirements-traceability-matrix.md`
- `roadmap.md`
- `demo-ready-checklist.md`
- `QUICK-REFERENCE.md`
- role-specific artifacts such as QA, security, support, or BugBot docs

Preserve intentionally historical documents if they are clearly marked as historical.
If they are not clearly historical, either update them to current state or add the historical context explicitly.

## Operating Rules

- Do not assume MVP-only scope.
- Do not preserve stale markdown just because it was created earlier.
- Distinguish API-backed capability from UI-backed capability.
- Distinguish implemented, partial, and not-started work honestly.
- Prefer small, test-backed implementation changes over broad rewrites.
- Update cross-references and counts when stories or statuses change.

## Role-Specific Use

### PO/BA
- Refresh stories, acceptance criteria, validation rules, and phase boundaries.

### Developer / Platform
- Reconcile docs with actual backend/frontend/test surfaces.
- Implement the smallest missing code or test changes needed to support truthful docs.

### QA / STE
- Reconcile artifact claims with actual test coverage and evidence.
- Add or repair tests where current claims are unsupported.

### Security / Verifier
- Reconcile security findings with current code and tests.
- Update docs and implement small hardening fixes if needed.

### Support / Triage
- Reconcile operational notes, commands, and diagnostics with the actual runtime contracts.

### BugBot
- Use current docs and code together to reproduce, narrow, and fix one concrete defect.

## Done Criteria

This skill is done when:

- broken or stale markdown claims are corrected
- related artifacts stay internally consistent
- implementation and test changes are made when required for truthfulness
- remaining gaps are called out explicitly rather than implied away