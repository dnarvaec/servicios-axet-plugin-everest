---
name: a11y-audit-foundation
description: 'Shared workflow for live accessibility audits with Playwright MCP. Use when creating or maintaining accessibility agents that need URL resolution, canonical artifact paths, main-content targeting, viewport discipline, overlay handling, or safe interaction rules.'
argument-hint: 'Audit scenario or agent being updated'
user-invocable: true
---

# A11y Audit Foundation

Use this skill when an accessibility workflow needs the common operational contract already repeated across the repo's microagents.

## Use Cases
- Create a new Playwright-based accessibility validator.
- Refactor an existing validator to reduce duplicated instructions.
- Align a validator with the shared `artifacts/a11y/<target-slug>/` conventions.
- Reuse the same URL-resolution, main-content, and safe-interaction rules across checks.

## What This Skill Standardizes
- WCAG scope guardrail: audit WCAG A and AA only unless a validator explicitly documents a narrower scope.
- Live target resolution for `http` and `https` URLs.
- Canonical `outputDir` and `screenshotDir` expectations.
- Minimal invocation contract for delegated validators.
- Reusable canonical report-contract template for report-writing accessibility microagents.
- Project-wide default language expectation for Markdown reports produced by report-writing accessibility microagents.
- Main-content extraction strategy for `main`, `[role="main"]`, dense content containers, and `body` fallback.
- Playwright navigation and stabilization guidance for desktop-first audits.
- Single-session coordination for multi-check validators that reuse one inventory or observation pass.
- Conservative interaction rules for overlays, forms, and risky workflows.
- Playwright MCP as the authoritative browser runtime for audit evidence.

## Invocation Contract (shared)
- Prefer a compact prompt: `target`, `outputDir`, `screenshotDir`, the concrete objective, and only strictly required scalar options.
- State explicitly that WCAG AAA is out of scope and that the audit must be limited to A/AA only.
- If a caller asks for AAA coverage, cap the effective scope at AA and record that normalization in the resulting limitations/report notes.
- In this project, report-writing accessibility microagents should be instructed to write persisted Markdown reports in Spanish unless the user explicitly requests another report language.
- Do not require serialized HTML, accessibility trees, screenshot manifests, long selector inventories, or repeated instruction blocks in the prompt.
- Keep delegated prompts small enough that the validator can reacquire the live page and derive its own inventory.

## Canonical Report Contract Template (shared)
Use this template when authoring or refactoring a report-writing accessibility microagent so the contract is referenced once here instead of redefined in full in every agent.

### Template goals
- Keep the chat contract compact and artifact-oriented.
- Keep canonical paths stable under `artifacts/a11y/<target-slug>/`.
- Keep Markdown requirements predictable without forcing every agent to repeat the same prose.
- Let each validator override only the parts that are genuinely validator-specific.

### Template: Output-path requirements
- `<target-slug>` MUST follow the same canonical derivation defined by `accessibilityAgent.agent.md`.
- The canonical stable report path is `{outputDir}/report-<validator-slug>.md`.
- The canonical stable JSON artifact is `{outputDir}/<validator-slug>-review.json`.
- Optional timestamped copies are supporting artifacts only; the stable files above remain canonical.

### Template: Console/Chat Output
- `status`: `PASS` | `WARN` | `FAIL`
- `resolvedFrom`: `user-url`
- `resolvedUrl`: target URL before navigation
- `finalUrl`: final URL after redirects
- `reportFile`: path to the canonical Markdown report
- `summary`: 1-3 bullets, or one bullet per check when the validator bundles several checks in one run
- Add optional fields such as `mainSelectorUsed`, `suggestion`, `injectionDecision`, or execution diagnostics only when they materially change interpretation.

### Template: Stable Artifacts
- Always list the two canonical files explicitly:
	- `{outputDir}/report-<validator-slug>.md`
	- `{outputDir}/<validator-slug>-review.json`
- Then list only the validator-specific supporting screenshots or evidence files.
- If the validator cannot complete meaningful checks, the canonical files must still be created and must explain the limitation.

### Template: Required Markdown shape
- Start with a single top-level title.
- Follow with a short metadata bullet list covering at least `Timestamp`, `Target URL`, and `Final URL`.
- Then use stable second-level headings for configuration, validator-specific results, findings, limitations, and evidence.
- Render scalar values as bullets; render findings as subheadings, bullets, or a table.
- Do not emit the final report as a naked `key: value` dump, console transcript, or snapshot wrapper.

### Template: Shared-report-contract hook
- After the validator-specific Markdown section, add a short `Shared Report Contract` subsection that points back to this skill and to `a11y-report-normalization` instead of restating the generic rules.
- Then add only validator-specific deltas, for example the required title, mandatory sections, or a fallback behavior that differs from the default.

### Authoring guidance
- Reuse this template verbatim when the agent needs `Output-path requirements`, `Console/Chat Output`, `Stable Artifacts`, or `Required Markdown shape`.
- Keep validator-specific prose focused on what changes: check inventory, evidence files, extra fields, or mandatory section names.
- If a validator needs a materially different contract, document only the delta from this template.

## WCAG Scope Guardrail (shared)
- Default audit scope is WCAG 2.2 levels A and AA only.
- WCAG AAA criteria are out of scope for the shared accessibility workflow unless a validator is intentionally authored for a separate AAA-only mode.
- Shared-orchestration prompts must not ask delegated validators to inspect, report, or remediate AAA-only success criteria.
- If a validator supports an explicit level parameter, pass `AA` as the maximum scope unless the run is intentionally constrained further to `A`.
- If a validator returns AAA-only findings despite the requested scope, drop that content from consolidated results and record the normalization as a limitation instead of surfacing it as canonical output.

## Navigation Readiness Policy (shared)
- `balanced` mode: wait for `domcontentloaded`, then confirm meaningful visible main content, then apply a short settle interval.
- `strict` mode: attempt `networkidle` with a bounded timeout, then still confirm meaningful visible main content before scanning; if `networkidle` stalls or content remains insubstantial, fall back to the `balanced` strategy.
- If a primary selector is known, wait for that selector before scanning.
- Never treat `networkidle` alone as sufficient readiness; always use bounded timeouts and record fallback usage in limitations.
- If the page is blocked (login wall, consent wall, 403/404, or blank page), return `FAIL` with explicit cause instead of continuing speculative checks.

## Agent Role Constraint (shared)
- Accessibility microagents are report-oriented, not remediation-oriented.
- Do not modify application source files.
- Any suggested fixes belong in the report output.

## Live Reacquisition Rule (shared)
- For live external pages, reacquire the page from `target`.
- Treat local artifact files as optional references only.
- Do not depend on `file://` artifacts as the primary runtime source.
- Do not treat VS Code integrated-browser state as authoritative audit state; reacquire the page in Playwright MCP before capturing canonical evidence.

## Browser Runtime Rule (shared)
- Accessibility audits in this project should run in Playwright MCP, not in the VS Code integrated browser tool family.
- Use integrated-browser tools only for explicitly requested manual exploration or as a documented fallback when Playwright MCP cannot run.
- If a fallback is used, record it as a limitation and avoid presenting the run as equivalent to the normal Playwright MCP path.

## Blocker Handling Policy (shared)
- Before deep checks, detect blockers such as login walls, consent walls, 403/404 error pages, and blank or inaccessible pages.
- If blocked, return `FAIL` with the explicit blocker cause and stop speculative checks.

## Multi-Check Session Pattern (shared)
- When multiple WCAG checks reuse the same discovered candidates, viewport baseline, or observation window, run them in one browser session.
- Build shared inventories once, record them in the report and JSON artifact, and reuse them across later phases.
- Do not re-navigate between phases unless the validator explicitly needs a second controlled pass such as a viewport change.
- When passive observation and active probing are mixed, complete the passive phase first if active probing could contaminate the baseline.
- Make phase order explicit only when the validator has criterion-specific constraints beyond this shared pattern.

## Safe Interaction Rules (shared)
- Prefer reversible interactions only: focus, hover, small keyboard probes, safe toggles, local viewport changes, and non-destructive field edits.
- Do not purchase, create real accounts, submit destructive workflows, intentionally expire sessions, or trigger irreversible external side effects.
- If the only way to confirm behavior requires risky submission, authentication, or privileged access, record a limitation instead of speculating.
- Keep overlays, consent handling, and form probing minimal and scoped to what the validator needs to prove.

## Consolidated Verdict Rule (shared)
- Compute final status as the worst individual check status.
- Any `FAIL` yields overall `FAIL`.
- If no `FAIL` exists but any `WARN` exists, overall status is `WARN`.
- Otherwise, overall status is `PASS`.

## Procedure
1. Resolve the target URL and reject non-web schemes.
2. Derive the canonical target slug and artifact root.
3. Reacquire the live page with Playwright MCP instead of relying on `file://` artifacts.
4. Identify the primary visible content area using the shared extraction strategy.
5. Apply only safe, reversible interactions and document any blockers as limitations.
6. Keep prompts to delegated validators minimal: target URL, `outputDir`, `screenshotDir`, the concrete objective, and only required scalar options.

## References
- [Common contracts](./references/common-contracts.md)
- [Playwright flow](./references/playwright-flow.md)