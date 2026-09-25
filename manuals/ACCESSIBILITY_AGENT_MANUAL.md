# Accessibility Agents Manual

This document provides a focused guide to the accessibility agents and shared accessibility skills available in this project.

---

## Table of Contents

- [Overview](#overview)
- [Accessibility Package](#accessibility-package)
- [Accessibility Agent](#accessibility-agent)
- [Specialized Validators](#specialized-validators)
- [Shared Accessibility Skills](#shared-accessibility-skills)
- [How to Use](#how-to-use)
- [Expected Outputs](#expected-outputs)
- [Important Rules](#important-rules)

---

## Overview

The accessibility tooling in this repository is split into:

- one orchestrator agent that runs the full accessibility audit flow
- multiple specialized validators focused on specific WCAG concerns
- shared a11y skills used to standardize audit flow, Playwright interaction policy, report normalization, and structural heuristics

The goal of this package is to support accessibility audits, validation, and remediation guidance for live web pages using Playwright MCP and structured accessibility artifacts.

---

## Accessibility Package

The `accessibility` installation package includes:

- `accessibility_agent`
- `alt_text_validator`
- `Consistency and Error Validation Agent`
- `Document Structure Inspector Agent`
- `Image Text Contrast Validator`
- `Language Validation Agent`
- `Media Accessibility Validator`
- `Tab Navigation Validator`
- `Text Spacing Validation Agent`
- `a11y-audit-foundation`
- `a11y-playwright-interactions`
- `a11y-report-normalization`
- `a11y-structural-heuristics`

Use this package when you need:

- end-to-end accessibility audits
- semantic accessibility validation
- keyboard and focus review
- language and document-structure checks
- timed-media accessibility checks
- text-spacing regression analysis
- remediation-oriented accessibility investigation with stable artifacts

---

## Accessibility Agent

### Overview

The **Accessibility Agent** is the orchestrator for accessibility reviews.

### Main Functionality

**Primary Purpose**: Run an end-to-end accessibility audit pipeline that renders the page, performs rule-based and semantic checks, proposes minimal remediation, and produces stable artifacts.

**Core Principle**: Reduce detected accessibility issues without breaking the UI, while keeping the run traceable through canonical JSON, Markdown, screenshot, and diff artifacts.

### What It Does

1. Renders the target in a real browser.
2. Runs rule-based validation with axe-core.
3. Runs semantic validation using delegated accessibility micro-agents.
4. Produces suggested remediation patches.
5. Revalidates when safe and allowed.
6. Writes canonical audit artifacts under `artifacts/a11y/<target-slug>/`.
7. Generates the final dashboard automatically once micro-agent execution and artifact consolidation are complete.

### Typical Use

```text
Run accessibility audit for https://example.com
```

```text
Audit accessibility for https://example.com and generate remediation suggestions
```

---

## Specialized Validators

### Alt Text Validator

Validates whether image alternative text matches the real rendered image content.

Best for:

- missing `alt`
- generic `alt`
- mismatched `alt`
- decorative images that should be empty

### Consistency and Error Validation Agent

Audits consistency across repeated UI patterns and form error handling.

Best for:

- repeated action consistency
- help affordance consistency
- required and invalid input errors
- error association and correction hints
- review-before-submit safeguards
- redundant data entry
- accessible authentication checks
- status message exposure
- name, function, and value exposure

### Document Structure Inspector Agent

Checks the structural quality of the visible main content.

Best for:

- heading hierarchy
- misuse of headings as paragraphs
- fake lists
- table semantics
- layout-table misuse
- minimum interactive target size and spacing

### Image Text Contrast Validator

Validates contrast for text rendered inside images.

Best for:

- hero banners with text over images
- promotional graphics
- CTA text rendered as pixels
- low-contrast text embedded inside images

### Language Validation Agent

Validates that the page language matches the predominant visible main content.

Best for:

- missing `lang`
- empty `lang`
- wrong language declaration
- mixed-language pages that need section-level `lang`

### Media Accessibility Validator

Audits timed media such as audio and video.

Best for:

- missing transcripts
- missing captions
- missing audio description
- unlabeled media
- autoplay audio without controls

### Tab Navigation Validator

Validates keyboard navigation and focus behavior.

Best for:

- tab order problems
- missing visible focus
- keyboard-inoperable controls
- menu keyboard issues
- keyboard traps
- mismatch between tab order and accessibility-tree order

### Text Spacing Validation Agent

Audits WCAG 1.4.12 text spacing behavior after runtime spacing overrides are applied.

Best for:

- clipping after spacing changes
- truncation after spacing changes
- horizontal overflow introduced by spacing overrides
- unreadable labels or controls after spacing changes

---

## Shared Accessibility Skills

### a11y-audit-foundation

Standardizes the common live-audit workflow used by the accessibility validators.

Use for:

- canonical output paths
- target URL resolution
- main-content selection
- safe interaction rules
- viewport discipline

### a11y-playwright-interactions

Standardizes the Playwright MCP runtime contract reused by accessibility agents.

Use for:

- deterministic readiness checks
- browser-context execution rules
- retry and fallback budgets
- snippet execution policy
- large-payload and wrapped-result handling

Mandatory policy:

- every accessibility agent or micro-agent that uses Playwright MCP must apply this skill as its runtime contract
- do not define ad hoc waits based on exact heading text or placeholder strings when the shared readiness contract already applies
- treat Playwright code execution as browser-context execution, not Node.js execution
- prefer inline self-contained snippets and treat `filename` execution as unsupported unless previously validated in the same runtime mode

### a11y-report-normalization

Standardizes report persistence and Markdown normalization.

Use for:

- canonical report filenames
- Markdown integrity rules
- fallback report writing
- stable JSON and Markdown outputs

### a11y-structural-heuristics

Standardizes reusable structural heuristics used by structural validators.

Use for:

- visible main-text extraction
- text-density heuristics
- evidence snippet selection
- heading, list, table, and language heuristics

---

## How to Use

### Install the Accessibility Package

```bash
python qa_mcp_servers.py install accessibility
```

### Typical Requests

**Run a full accessibility audit**
```text
Run accessibility audit for https://example.com
```

**Check document language**
```text
Validate the page language for https://example.com
```

**Check keyboard navigation**
```text
Validate tab navigation for https://example.com
```

**Check text spacing regressions**
```text
Run text spacing validation for https://example.com
```

**Check media accessibility**
```text
Audit media accessibility for https://example.com
```

### When To Use The Orchestrator Vs. A Specialized Validator

- Use `accessibility_agent` when you want the full audit pipeline and consolidated outputs.
- Use a specialized validator when the problem is already known and you want focused evidence for a single accessibility concern.

---

## Expected Outputs

The accessibility package is designed to produce stable artifacts under:

```text
artifacts/a11y/<target-slug>/
```

Depending on the validator used, outputs can include:

- Markdown reports
- JSON review files
- accessibility snapshots
- DOM captures
- screenshots
- suggested remediation diffs
- changelog and limitations files

Common examples:

- `report-before.json`
- `report-after.json`
- `dashboard.html`
- `uncovered_criteria.md`
- `report-language.md`
- `report-document-structure.md`
- `report-media-accessibility.md`
- `report-tab-navigation.md`
- `report-text-spacing.md`
- `suggested-patch.diff`

---

## Important Rules

- Do not treat a partial or blocked accessibility run as a full pass.
- Prefer explicit limitations over guessed conclusions.
- Keep remediation suggestions minimal and traceable.
- Use the orchestrator for consolidated audits and micro-agents for focused checks.
- All Playwright-based accessibility agents must use `a11y-playwright-interactions` as the runtime policy source of truth.
- Do not reintroduce local Playwright heuristics for readiness, browser-context behavior, or retry budgets unless the agent documents a validator-specific delta.
- Do not assume Playwright snippets have access to Node.js globals such as `require`, `fs`, or `path`.
- Do not rely on `filename` execution for Playwright snippets unless that exact tool/file mode has already been validated.
- Default to isolated reacquisition per viewport on live external pages, especially before keyboard, focus, or navigation-sensitive phases.
- Require selector preflight before active interactions or element screenshots: exactly one visible actionable candidate, or a documented limitation.
- Keep validator evidence under the canonical `outputDir` and precreate screenshot directories before capture attempts.
- Prefer explicit phase budgets for expensive validators over open-ended local exploration.
- Preserve canonical report filenames and artifact locations.
- Normalize Markdown reports before considering them final.
- Generate the dashboard only after all micro-agents finish and the canonical artifacts are already consolidated.
- Do not rely on local `file://` artifacts for live external page validation when the micro-agent contract requires reacquiring the live page.

---

## Summary

| Component | Primary Use |
|-------|------------|
| **Accessibility Agent** | Full accessibility audit orchestration |
| **Alt Text Validator** | Alternative text quality and image meaning checks |
| **Consistency and Error Validation Agent** | Consistency, form errors, input assistance, and status messaging |
| **Document Structure Inspector Agent** | Headings, lists, tables, and target spacing |
| **Image Text Contrast Validator** | Contrast of text embedded in images |
| **Language Validation Agent** | Language-of-page validation |
| **Media Accessibility Validator** | Transcript, captions, audio description, and autoplay-audio checks |
| **Tab Navigation Validator** | Keyboard navigation and focus behavior |
| **Text Spacing Validation Agent** | WCAG 1.4.12 text spacing regressions |
