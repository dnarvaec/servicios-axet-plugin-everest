# Playwright Flow

## Default Execution Pattern
1. Start desktop viewport first.
2. Navigate to the live target.
3. Wait for `domcontentloaded` and meaningful content.
4. Stabilize briefly for client-side rendering.
5. Capture screenshots or DOM only after the page is usable.

## Evidence Collection
- Prefer screenshots and DOM collected from the current live page.
- Keep browser actions sequential when they mutate focus, layout, or page state.
- Reuse the canonical `outputDir` tree for saved evidence.

## Delegation Guidance
- Use minimal prompts for subagents to avoid request bloat.
- Do not inline DOM dumps, axe JSON, or accessibility-tree payloads unless strictly required.
- Treat each delegated Playwright run as self-contained.