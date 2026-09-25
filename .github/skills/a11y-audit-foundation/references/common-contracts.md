# Common Contracts

## WCAG Scope Guardrail
- Shared accessibility audits are limited to WCAG levels A and AA.
- Treat AAA as out of scope unless a validator has been intentionally authored for a separate AAA-only workflow.
- When a caller asks for AAA coverage, normalize the effective scope back to AA and record that normalization in limitations or report notes.
- Delegated prompts should explicitly say that AAA criteria must not be audited, reported, or remediated.
- When a validator supports an explicit level/tag parameter, pass AA as the maximum scope unless the parent run is intentionally narrower.

## Target Resolution
- Accept full `http://` or `https://` URLs as-is.
- Reject `file:`, `javascript:`, `data:`, and similar non-web schemes.
- If local artifacts are mentioned, treat them as optional references after live navigation succeeds.

## Canonical Output Layout
- Base directory: `artifacts/a11y/<target-slug>/`
- Screenshots directory: `{outputDir}/screenshots/`
- Stable artifacts overwrite prior runs unless the caller explicitly preserves history.

## Target Slug Convention
- Lowercase host and path.
- Replace dots in host with `-`.
- Use `root` for `/`.
- Join path segments with `-`.

## Main Content Strategy
1. `main`
2. `[role="main"]`
3. Highest text-density candidate among `article`, `section`, `div`
4. `body` excluding `nav, header, footer, aside, form, script, style`

## Safe Interaction Rules
- Do not log in, submit destructive actions, purchase, or guess credentials.
- Dismiss cookie banners only when trivial and reversible.
- Prefer inspection over interaction.
- When validation requires risky state changes, stop and write a limitation instead of guessing.