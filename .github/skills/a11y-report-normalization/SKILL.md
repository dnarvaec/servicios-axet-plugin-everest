---
name: a11y-report-normalization
description: 'Normalize accessibility audit outputs into stable Markdown and canonical artifacts. Use when creating or maintaining agents that must enforce Markdown integrity gates, fallback report payloads, or stable report filenames.'
argument-hint: 'Report file or validator being normalized'
user-invocable: true
---

# A11y Report Normalization

Use this skill when a validator writes Markdown or JSON artifacts that must remain stable and machine-consumable.

## Use Cases
- Add a new report-writing microagent.
- Refactor repeated Markdown integrity rules.
- Normalize wrapper-like Playwright outputs into plain Markdown.
- Align canonical report filenames and fallback behaviors.

## What This Skill Standardizes
- Stable report naming under `artifacts/a11y/<target-slug>/`.
- Canonical stable-report and stable-JSON contracts.
- Default human-language policy for Markdown accessibility reports.
- Markdown integrity checks before finalizing a report.
- Compact console/chat output that points to persisted artifacts.
- Inline fallback behavior when file writes fail.
- Separation between canonical files and optional supporting artifacts.

## Report Language Policy (shared)
- In this project, Markdown reports produced by accessibility validators default to Spanish.
- This rule applies to canonical `.md` files, timestamped Markdown copies, and inline-fallback `reportMarkdown` payloads.
- Write headings, metadata bullets, section titles, summaries, findings, notes, limitations, and remediation guidance in Spanish unless the user explicitly requests another report language.
- Preserve quoted UI strings, proper nouns, code, selectors, URLs, and evidence snippets in their original language when needed for accuracy.
- JSON artifacts may remain language-neutral or use stable field names in English when that is better for machine consumption.

## Canonical Artifact Contract (shared)
- Each validator should expose one canonical Markdown report path and one canonical JSON artifact path under `artifacts/a11y/<target-slug>/`.
- Optional timestamped copies, alternate views, or richer originals may exist, but they are supporting artifacts and must not replace the stable filenames.
- If a validator emits extra screenshots or evidence indexes, keep them additive and aligned to the same canonical output directory.

## Compact Output Shape (shared)
- Keep chat output skimmable and artifact-oriented.
- Prefer this common shape unless the validator truly needs extra fields: `status`, `resolvedFrom`, `resolvedUrl`, `finalUrl`, `reportFile`, and `summary`.
- Add optional fields such as `suggestion`, `mainSelectorUsed`, or execution diagnostics only when they materially change interpretation.
- If file persistence fails, return `reportWriteStatus: inline-fallback`, the intended canonical `reportFile`, and normalized `reportMarkdown` so the caller can persist or reconcile the fallback payload deterministically.
- Do not replay the full report body, full findings tables, raw snapshots, or exhaustive inventories in chat when the canonical report file already contains them.

## Procedure
1. Normalize wrapped, snapshot-like, or otherwise malformed report content before persistence.
2. Ensure the normalized Markdown report body is written in Spanish unless an explicit report-language override exists.
3. Write the canonical report file directly when possible.
4. Keep the stable Markdown and stable JSON paths authoritative even when timestamped copies also exist.
5. Validate the normalized saved Markdown against the shared integrity gate.
6. If persistence fails, return `reportWriteStatus: inline-fallback`, the intended canonical `reportFile`, and normalized `reportMarkdown`.
7. Keep JSON artifacts machine-readable and aligned with the stable report names.

## References
- [Markdown integrity gate](./references/markdown-gate.md)
- [Canonical artifacts](./references/canonical-artifacts.md)