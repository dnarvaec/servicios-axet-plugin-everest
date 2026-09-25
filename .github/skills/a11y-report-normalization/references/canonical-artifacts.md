# Canonical Artifacts

## Stable Output Principles
- Canonical files represent the latest authoritative run.
- Supporting artifacts may be richer or timestamped, but they do not replace the stable aliases.
- When a subagent produces both a stable alias and a richer original, preserve both when useful.

## Naming Discipline
- Keep report names predictable, for example `report-language.md` or `report-document-structure.md`.
- Keep paired machine-readable outputs beside the report when a validator defines them.
- Keep screenshots under `{outputDir}/screenshots/` unless a validator explicitly needs a deeper subdirectory.