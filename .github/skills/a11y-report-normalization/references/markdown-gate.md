# Markdown Integrity Gate

## Required Shape
- Start with one top-level heading.
- Follow with metadata rendered as bullets.
- Use named sections such as `Summary`, `Findings`, `Evidence`, `Notes`, or `Limitations`.
- Use tables only when they improve readability.

## Required Language
- For this project, the saved Markdown report MUST be written in Spanish unless the user explicitly requests another report language.
- Section headings, metadata labels, narrative findings, notes, and limitations MUST therefore be in Spanish.
- Preserve original-language UI strings, code, selectors, and exact quoted evidence only where fidelity requires it.

## Forbidden Patterns
- Free-standing `status:`, `url:`, or `timestamp:` body lines.
- Snapshot wrappers such as `generic [ref=`.
- Console wrappers like `Total messages`, `[ERROR]`, `[WARNING]`, or `Call log`.
- JSON-stringified Markdown with escaped newlines or escaped headings.

## Fallback Rule
- If the runtime cannot write files, return the intended canonical path plus the full normalized Markdown payload.
- Do not claim success writing the canonical file when fallback was used.
- The fallback Markdown payload MUST also follow the same Spanish-language requirement.