---
name: a11y-playwright-interactions
description: 'Shared Playwright MCP interaction policy for accessibility agents. Use when creating or maintaining validators that need deterministic page readiness, safe browser-context execution, retry/fallback rules, or large-payload handling.'
argument-hint: 'Accessibility validator or Playwright flow being created, reviewed, or refactored'
user-invocable: true
---

# A11y Playwright Interactions

Use this skill when a Playwright-based accessibility workflow needs a shared runtime contract instead of ad hoc waits, retries, or snippet execution rules.

## Use Cases
- Create or refactor a Playwright-based accessibility validator.
- Standardize readiness checks across several microagents.
- Prevent browser-context mistakes such as `require is not defined`.
- Normalize retry, fallback, and limitation handling for unstable live pages.
- Define how large Playwright payloads should be captured and persisted.

## Example Requests
- "Update a Playwright validator so it stops waiting on unstable heading text and uses shared readiness rules."
- "Refactor a browser-run snippet that currently assumes `require` or filesystem access."
- "Harden a microagent against repeated `413` failures and ambiguous fallback behavior."

## What This Skill Standardizes
- Readiness policy based on meaningful visible content instead of brittle selector text.
- Browser-context execution rules for `mcp_playwright_browser_run_code` and `mcp_playwright_browser_run_code_unsafe`.
- Screenshot capture rules for page-level versus element-level evidence.
- Preferred snippet shape: inline, self-contained functions over implicit `filename` execution.
- Unified failure classification: `transient`, `blocked`, `capability-exhausted`, `environmental`.
- Retry budgets and fallback rules for navigation, stabilization, and delegated microagent calls.
- Opportunistic-interaction rules so invisible consent controls do not become pseudo-blockers.
- Reacquisition rules for active probes that are sensitive to reloads, focus drift, or destroyed execution contexts.
- Selector preflight rules before active interactions or element screenshots.
- Evidence-path rules for screenshot and JSON persistence under canonical output roots.
- Phase-budget defaults for validators with historically expensive active probes.
- Payload-size handling, wrapped-result normalization, and explicit limitation recording.
- Multi-viewport isolation and state reset rules.

## Readiness Contract
- Do not treat `networkidle` alone as sufficient.
- Default readiness sequence is:
  1. wait for `domcontentloaded`
  2. resolve only the blockers needed for safe observation, such as cookie banners or consent overlays
  3. confirm meaningful visible content in `main`, `[role="main"]`, or the densest visible content container
  4. apply a short bounded settle window
- Prefer observable content signals over brittle text matches. Examples of valid readiness signals:
  - visible main container exists and is not hidden
  - main-content text length is materially non-trivial
  - at least one visible heading, paragraph block, list, table, or interactive cluster exists in the primary content area
- Do not wait on exact `h1` text, placeholder strings like `Loading...`, or one-off shell markers unless the validator has a documented site-specific reason.
- If readiness remains uncertain after one bounded attempt, capture the best available evidence, record the limitation, and continue with a partial run instead of repeating the same heuristic indefinitely.

## Opportunistic Interaction Policy
- Distinguish required interactions from opportunistic interactions before attempting them.
- Required interactions are the smallest reversible actions needed to expose the content or state being audited.
- Opportunistic interactions are convenience actions such as dismissing a cookie banner that is not actually blocking the primary content, expanding non-essential marketing drawers, or trying alternate entry points that only improve page cleanliness.
- Before any click or tap attempt, verify that the candidate control is visible, enabled, and stable enough to receive the action.
- Do not click a locator just because it exists in the DOM.
- If an opportunistic control is present but not visible or not safely actionable, skip it, record a limitation only when it materially affected evidence quality, and continue with the audit.
- If a required interaction is not visible or not safely actionable, allow one bounded recovery attempt and then degrade to a blocked or partial result instead of repeating the same click.

## Selector Preflight Rule
- Before `click`, `tap`, `hover`, `focus`, keyboard activation, or element-scoped screenshot capture, verify the target selector resolves to exactly one actionable candidate in the current state.
- Actionable means all of the following: present, visible, enabled when applicable, stable enough to receive the action, and specific enough that the agent can explain why that candidate was chosen.
- Treat `0` matches and `>1` matches as different failures:
  - `0` matches: treat as state drift, wrong assumption, or stale selector; reacquire or downgrade once instead of retrying the same selector unchanged.
  - `>1` matches: treat as an ambiguity bug in the probe; narrow the selector, choose a documented visible subset, or degrade to a limitation.
- Do not treat Playwright strict-mode violations as transient transport noise. They are selector-shape failures and must trigger selector repair or a bounded fallback.
- When an ambiguity cannot be resolved safely, capture page-level or container-level evidence and record the limitation instead of forcing an arbitrary click.

## Browser Execution Model
- Code executed via `mcp_playwright_browser_run_code` or `mcp_playwright_browser_run_code_unsafe` runs in browser/page context.
- Do not assume Node.js modules or globals such as `require`, `fs`, `path`, `process`, or workspace-relative filesystem access.
- Return only JSON-serializable values or bounded strings from browser-executed snippets.
- If the result is large, prefer explicit chunking or persistence outside the browser context after the tool call.
- If a script dependency must be loaded in-page, verify availability before use and return an explicit machine-readable error payload when loading fails.

## Tool-Specific Invocation Contract
- Do not treat all Playwright MCP tools as interchangeable. A calling pattern that is valid for screenshots is not automatically valid for `mcp_playwright_browser_evaluate`, snapshots, or browser-run code.
- Choose the tool by execution shape, not just by intent:
  - `mcp_playwright_browser_take_screenshot`: screenshots only
  - `mcp_playwright_browser_evaluate`: short DOM reads or small computed values scoped to a real selector or a safe document container
  - `mcp_playwright_browser_run_code` or `mcp_playwright_browser_run_code_unsafe`: multi-step browser logic, injected libraries, iterative DOM processing, or code that would be brittle as an inline evaluate expression
- Treat any cross-tool parameter reuse as suspect until the exact tool contract has been validated.
- Before issuing a new Playwright MCP call shape in an orchestrator, prefer an already documented calling pattern from this skill over improvising a new variant.

## Evaluate Contract
- Use `mcp_playwright_browser_evaluate` only for short, page-read operations that return a compact JSON-serializable value.
- When the call is logically page-level, prefer a real container selector such as `body`, `main`, or another documented primary container instead of pseudo-targets.
- Never use `target: "page"`, `element: "page"`, or another screenshot-style pseudo-element with `mcp_playwright_browser_evaluate`.
- Do not use `mcp_playwright_browser_evaluate` for code that needs complex escaping, multiple helper blocks, loops over large node sets, injected libraries, or large intermediate state.
- If the intended logic is more than a short expression or a small inline function, switch to `mcp_playwright_browser_run_code` or `mcp_playwright_browser_run_code_unsafe` instead of stretching `evaluate`.
- Treat selector-free page reads as a contract exception that must be explicitly supported by the tool mode; otherwise, anchor the read to `body` or another real container.

## Snippet Envelope Contract
- Default shape: an inline, self-contained async function that receives all needed inputs explicitly and returns a compact JSON-serializable object.
- Do not rely on implicit globals beyond normal browser primitives. If the snippet needs `document`, `window`, `location`, or injected libraries, reference them as browser-context objects and validate availability first.
- If a snippet computes reusable data such as axe results, DOM fragments, candidate inventories, or focus traces, store the payload on a deterministic page-global key and return only a status envelope from the initial call.
- Use one follow-up persistence step outside the browser snippet to read and save the payload. Do not mix heavy computation, file writes, and report formatting in one browser call.
- Treat `ReferenceError: window is not defined`, `ReferenceError: document is not defined`, and `ReferenceError: require is not defined` as contract violations in snippet shape. Fix the snippet or switch to the shared persistence recipe instead of retrying unchanged code.
- Treat JavaScript parse failures such as `SyntaxError: Unexpected token ')'` as snippet-shape violations, not transient page failures. Repair the snippet shape or move the logic to `mcp_playwright_browser_run_code_unsafe` instead of retrying the same `evaluate` form.

## Screenshot Capture Policy
- Treat full-page screenshots and element screenshots as different modes. Do not combine them in the same call.
- When the goal is a full-page artifact, request a page-level screenshot with `fullPage: true` and do not pass an element target or element-scoped screenshot request.
- When the goal is an element artifact, target the specific element and keep `fullPage: false`.
- If the evidence surface is larger than one element but smaller than the full page, prefer a dedicated container element screenshot or a computed clip rectangle instead of forcing `fullPage: true` on an element capture.
- When a previous snapshot reference may be stale after navigation, resize, or DOM mutation, reacquire the snapshot before taking an element screenshot instead of reusing the old reference.
- Treat errors such as `fullPage cannot be used with element screenshots` or `Ref ... not found in the current page snapshot` as invocation-shape problems. Fix the screenshot mode or reacquire the target instead of retrying the same call unchanged.
- Preferred calling patterns:
  - full-page evidence: `element: "page"`, empty target, `fullPage: true`
  - element evidence: explicit element target, `fullPage: false`
- Forbidden calling patterns:
  - do not use `target: "page"` for full-page screenshots
  - do not combine `fullPage: true` with an explicit element selector or element snapshot reference
  - do not repair a stale element reference by broadening to `fullPage: true` on the same element-scoped call

## Evidence Path Contract
- Treat `outputDir` as the canonical root for all persisted validator artifacts.
- Treat `screenshotDir` as the only allowed root for validator-owned screenshots unless the caller explicitly documents another child directory under `outputDir`.
- Create the screenshot directory before the first capture attempt. Do not assume element or page screenshot tools will create intermediate directories for you.
- Do not write screenshots, JSON, or Markdown evidence outside the canonical output tree for the run.
- Treat `File access denied`, `outside allowed roots`, and `ENOENT` during evidence capture as path-contract failures. Repair the path or precreate the directory before retrying.

## Persistence Recipe For Browser Snippets
- Do not attempt to write workspace files from browser snippets with `require('fs')`, `fs.writeFileSync`, or similar Node-only patterns.
- Preferred persistence flow for large or reusable payloads:
  1. compute the payload in the page,
  2. store it on `window.__copilot*` or another deterministic page-global key when the payload must survive one follow-up call,
  3. return only a compact status object from the snippet,
  4. persist the stored payload outside the browser snippet using a workspace-aware tool such as `mcp_playwright_browser_evaluate` with `filename`, `create_file`, or a terminal/workspace file write.
- Example safe pattern for axe or DOM capture:
  - run the expensive browser-side computation in `mcp_playwright_browser_run_code_unsafe`,
  - set `window.__axeResults = results` or `window.__domCapture = html`,
  - then call `mcp_playwright_browser_evaluate` with `() => window.__axeResults` or `() => window.__domCapture` and save that result through `filename` or a workspace tool.
- If the payload is too large even for that handoff, split it deterministically before returning or persisting it, for example by viewport, rule, or candidate range.
- Treat `ReferenceError: require is not defined` as a browser-context contract violation, not as a transient site failure; fix the snippet shape instead of retrying the same code.

## Snippet Execution Policy
- Preferred pattern: pass `code` as an inline, self-contained async function.
- Treat `filename` as unsupported by default unless the specific tool invocation mode has already been validated for that file shape.
- Do not assume that providing a workspace file path means the tool will execute it as Node.js, inject it into the page, or persist artifacts automatically.
- When using injected libraries such as axe-core:
  - verify the library is present before calling it
  - return an explicit error object if injection or execution fails
  - document fallback behavior instead of silently swallowing the failure

## Failure Classification
- `transient`: short-lived issue that is worth one bounded retry, such as a detached element or a one-off transport failure.
- `blocked`: the page or check cannot proceed meaningfully because of a login wall, consent wall, blank state, missing permissions, or another explicit blocker.
- `capability-exhausted`: the tool/runtime cannot safely complete the check, such as repeated payload-size failures or unsupported browser-context behavior.
- `environmental`: external dependency failure such as blocked CDN, proxy interference, or missing local capability.

## Retry And Fallback Policy
- Give each phase a bounded retry budget. Default policy:
  - navigation/readiness: one retry after a small stabilization delay
  - live interaction blocked by overlay: one retry after a minimal safe dismissal attempt
  - transport-size failure such as `413`: one retry with smaller scope
  - delegated subagent returns `Sorry, no response was returned.`: one retry with a shorter prompt and smaller payload
  - same-heuristic readiness failure: do not retry more than once
- After the retry budget is exhausted, degrade to a partial result and record the limitation in canonical artifacts.
- Do not keep exploring new speculative waits if the check already has enough evidence to classify the limitation.

## Known Invocation-Error Repair Rules
- Treat the following errors as deterministic contract violations with a fixed repair path, not as generic transient failures:
  - `Error: "page" does not match any elements.`
  - `Error: fullPage cannot be used with element screenshots.`
  - `SyntaxError: Unexpected token ')'` during `mcp_playwright_browser_evaluate`
- Required repair mapping:
  - `"page" does not match any elements` in `mcp_playwright_browser_evaluate`: replace the pseudo-target with `body`, `main`, or another real container selector, or move the logic to `mcp_playwright_browser_run_code` / `mcp_playwright_browser_run_code_unsafe` if the read is genuinely page-level
  - `fullPage cannot be used with element screenshots`: change the call to the full-page screenshot pattern `element: "page"`, empty target, `fullPage: true`, or switch to a true element screenshot with `fullPage: false`
  - `SyntaxError: Unexpected token ')'`: do not retry the same serialized `evaluate` snippet; simplify the expression immediately or migrate the logic to `mcp_playwright_browser_run_code_unsafe`
- After one contract-repair attempt, do not keep varying the same broken shape. Either continue with the known-good pattern or downgrade with an explicit limitation.

## Active Probe Reacquisition Rule
- Treat focus-order checks, keyboard-entry checks, reload-sensitive navigation checks, and similar active probes as context-sensitive phases.
- Before starting a context-sensitive phase, prefer a freshly reacquired page or tab over a heavily mutated one when the earlier phases used reloads, dynamic DOM mutation, or multiple overlay probes.
- If a validator keeps one page alive across phases, it must explicitly reset the target URL and rerun the readiness contract before active probing begins.
- If `Execution context was destroyed` appears during an active phase, allow one clean reacquisition and rerun that phase once before downgrading to a limitation.

## State Restoration Ladder
- When a validator mutates page state during a reversible probe, use this recovery order before broadening scope:
  1. restore the local component state if possible, such as closing a popover, removing a temporary style injection, clearing focus, collapsing a panel, or undoing a non-destructive toggle
  2. if local restoration is not reliable, reset the page to `target` and rerun the readiness contract
  3. if the reset still leaves the phase unstable, reacquire one fresh page or tab and retry that phase once
- Do not chain multiple reacquisitions for the same phase.
- Record which recovery level was needed whenever it materially affects confidence, coverage, or reproducibility.
- Prefer this ladder over ad hoc phase-specific retries when the issue is contaminated state rather than a missing element or transport failure.

## Multi-Viewport And Session Rules
- Do not run multiple `axe.run()` executions concurrently against the same page/tab.
- Default to isolated reacquisition per viewport on external, dynamic, or hydration-heavy pages.
- For desktop-plus-mobile audits, prefer two controlled passes: acquire desktop evidence on a fresh page, then reacquire or reset for mobile before any resize-sensitive capture or active probe.
- If the same page/tab is reused, reset the page to the target URL and rerun the readiness contract before the next viewport check.
- Treat delegated Playwright microagent runs as self-contained. Do not rely on page state surviving across calls.

## Phase Budget Defaults
- Treat retry budgets and work budgets as separate controls. A validator can stay within retry budget and still exceed a sensible amount of work.
- Parent orchestrators should pass only the scalar budgets the validator needs. Validators should not invent larger budgets locally without documenting the delta.
- Recommended orchestrator-pass values for canonical runs of historically expensive active probes (agent internal defaults are noted when they differ from the canonical recommendation):
  - tab navigation: `maxTabs=25`, `maxKeyboardFlows=5`, `actionTimeoutMs=8000`
  - navigation predictability: `maxFindings=12`, `maxLinksToSample=12`, `maxControlsToProbe=8`, `actionTimeoutMs=8000`
  - visual resilience: `maxFindings=12`, `focusProbeTabs=15`; the agent mandates three separate viewport contexts (desktop, narrow 320 px, mobile 390 px) plus at most one text-spacing CSS injection pass — budget for four effective measurement contexts, not two
  - consistency and error validation: `maxForms=5`, `maxSteps=4` (agent internal defaults; pass a lower value only when the page has unusually complex or risky forms)
  - pointer interaction: agent internal defaults are `maxCandidates=20` and `maxTriggersToProbe=20`; for canonical runs on typical pages, passing `maxCandidates=12` and `maxTriggersToProbe=12` keeps the run bounded without under-sampling hover/gesture-rich pages
  - image-text contrast: `maxImages=4` on the first pass; reduce to `maxImages=2` on a bounded `413` retry
- When a phase budget is exhausted, stop broad exploration, persist the best evidence already collected, and record the limitation as `partial` rather than silently continuing.

## Payload Handling
- Anticipate wrapped Playwright results and normalize them before parsing.
- Persist raw companion artifacts before normalization when the tool result is large, ambiguous, or likely to be reused.
- Use bounded output shapes for browser snippets; avoid returning full DOM inventories when a filtered summary is sufficient.
- When a large payload must be preserved, split it deterministically by viewport, rule, or candidate set instead of returning one oversized blob.

## Required Limitation Recording
- Any fallback, retry exhaustion, blocked execution, or runtime mismatch must be reflected in canonical JSON or Markdown artifacts.
- Never convert an incomplete check into an implicit PASS.
- If the run continues in partial mode, keep the limitation machine-readable and tie it to the affected phase.

## Authoring Guidance
- Reference this skill from orchestrators and microagents instead of redefining the same Playwright rules inline.
- Keep validator-specific instructions focused on the check logic, not on generic runtime policy.
- When an agent needs a narrower rule than this skill, document only the delta.
- When a microagent includes its own reset or reacquisition wording, keep it to the phase-specific trigger or exception rather than restating the full recovery ladder.

## References
- [A11y Audit Foundation](../a11y-audit-foundation/SKILL.md)
- [A11y Report Normalization](../a11y-report-normalization/SKILL.md)