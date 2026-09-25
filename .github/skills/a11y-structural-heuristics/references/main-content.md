# Main-Content Heuristics

## Scope Selection
1. `main`
2. `[role="main"]`
3. Dense `article`, `section`, or `div`
4. `body` fallback with repetitive layout regions excluded

## Density Signals
- More visible characters than links.
- Continuous prose or coherent grouped items.
- Less repeated navigation chrome.

## Text Normalization
- Collapse whitespace.
- Remove empty lines.
- Skip obviously repeated or very short menu-like fragments.
- Cap evidence snippets so reports remain readable.