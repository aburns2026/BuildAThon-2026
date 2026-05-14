# BugBot Defect Record

Date: 2026-05-14
Defect Type: UI test strict-mode selector collision
Status: Resolved

## Summary

Playwright previously failed on the clock-out success assertion because a broad text selector matched more than one element in strict mode.

## Fix Applied

- Status assertions were scoped to the dedicated message element.
- Audit assertions remained scoped to the audit section.

## Current Verification

- Main-path Playwright flow passes.
- The broader Playwright suite now passes with 5 tests.

## Residual Risk

- Future selector changes should stay anchored to named regions, roles, or dedicated status containers rather than global text searches.
