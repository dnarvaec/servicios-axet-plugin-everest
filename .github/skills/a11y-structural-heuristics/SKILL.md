---
name: a11y-structural-heuristics
description: 'Shared heuristics for structural accessibility analysis. Use when building or refining validators that inspect main-content language, heading hierarchy, list semantics, table semantics, text density, or evidence snippets.'
argument-hint: 'Structural or language-analysis task'
user-invocable: true
---

# A11y Structural Heuristics

Use this skill for validators whose value comes from DOM heuristics and evidence selection rather than from multi-step interactive flows.

## Best Fit
- Language detection from visible main text.
- Document-structure inspections.
- Other low-risk structural checks that reuse text-density or evidence-snippet logic.

## What This Skill Standardizes
- Main-content text extraction and normalization.
- Text-density heuristics for choosing the analysis scope.
- Evidence-snippet selection that avoids dumping full DOM or long text.
- Reusable structural rules for headings, lists, tables, and language dominance.

## Procedure
1. Choose the main content with the shared extraction strategy.
2. Normalize visible text and remove repetitive UI fragments.
3. Run the specific heuristic set for structure or language.
4. Record concise evidence with short snippets and selector hints.
5. Prefer `WARN` over speculative `FAIL` when evidence is partial.

## References
- [Main-content heuristics](./references/main-content.md)
- [Document and language checks](./references/document-language.md)