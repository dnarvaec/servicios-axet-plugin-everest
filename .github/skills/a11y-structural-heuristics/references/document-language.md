# Document And Language Checks

## Language Heuristics
- Read `document.documentElement.lang` first and classify `MISSING` or `EMPTY` explicitly.
- Compare the declared language against the dominant language of normalized visible text.
- Split long text into chunks and aggregate by dominant base language.
- Treat mixed-language pages conservatively and recommend section-level `lang` when needed.

## Heading Heuristics
- Prefer a coherent outline with one main `h1`.
- Flag repeated level skips or headings used as paragraph-like prose.
- Include selector hints and short text snippets only.

## List And Table Heuristics
- Detect visual lists that are not semantic lists.
- Distinguish data tables from layout tables before judging semantics.
- Check headers, captions, `scope`, `headers`, and misuse of data-table semantics.