---
name: alt_text_validator
description:
  Validates whether image alternative text (alt/aria-label/aria-labelledby) matches the real image content using rendered DOM + screenshot context. Produces actionable, minimal suggestions aligned to WCAG 2.2 (1.1.1).
tools: [agent, 'playwright/*', 'web/fetch', 'qa_mcp_server/*']
---

## Goal
Given a live page identified by `page_url` and, when available, the current Playwright page, validate that meaningful images have appropriate alternative text and that any provided `alt` / `aria-label` matches the actual rendered visual content.

This microagent is designed to be called by `accessibility_agent` during the **Semantic scan** stage.

## Shared References

This micro-agent remains the runtime entry point for alt-text and image-label audits. For maintenance and future refactors, reuse this shared skill instead of duplicating common guidance again:
- [A11y Audit Foundation](../skills/a11y-audit-foundation/SKILL.md)

---

## Inputs
The caller (usually `accessibility_agent`) provides only lightweight parameters.

The microagent SHOULD be able to reacquire the live page from `page_url` when needed. If the caller already has the correct Playwright page open, the microagent MAY reuse it.

- `page_url` (required): live page URL for self-acquisition. If the current page URL is different, the agent MAY navigate to `page_url`.
- `candidates` (optional): list of candidate selectors/locators to evaluate (best-effort). If not provided, the agent must discover candidates from the live DOM.
- `locale` (optional): language used for suggested alternative text.
- `constraints` (optional):
  - `max_items` (default 12): cap items evaluated to avoid huge pages.
  - `prefer_empty_alt_for_decorative` (default true)
  - `do_not_suggest_new_copy` (default false): if true, only flag problems; do not propose specific wording.
  - `prefer_rendered_crop` (default true): capture a rendered crop for each candidate via Playwright.
  - `crop_output_dir` (optional): directory to save per-element crop screenshots (default: `artifacts/a11y/_alttext-crops/`).

Sampling requirement:
- Canonical runs MUST review exactly 12 image candidates when 12 or more eligible candidates are present.
- If fewer than 12 eligible candidates exist, review all eligible candidates and record that the page did not provide a full 12-item sample.
- When more than 12 eligible candidates exist, select a deterministic, stable 12-item sample so repeated runs on the same page are comparable.

Canonical identity requirement:
- Before sampling, the microagent MUST freeze one canonical candidate inventory from the current live DOM and assign each candidate a stable audit identity.
- Stable identity priority MUST be:
  1. existing element `id`
  2. normalized stable image URL or `src`
  3. normalized `tag + role + accessible name + nearest heading`
  4. normalized `tag + stable class subset + nearest heading`
- For canonical output, the microagent MUST NOT degrade a reviewed item to a positional selector such as `>> nth=0` when a higher-stability identity is available.
- If a candidate later detaches or reflows and can no longer be matched by its frozen identity, keep the original item identity, mark that item `needs-review`, and explain the rematch failure. Do not silently substitute a different node into the same review slot.

### Path safety contract for crop files
- When `constraints.crop_output_dir` is provided by the caller, it SHOULD be an absolute workspace path.
- Before writing the first crop, the microagent MUST:
  - resolve `crop_output_dir` to one concrete filesystem directory,
  - create the directory if it does not exist,
  - join filenames against that directory explicitly, never by relying on the current working directory.
- The microagent MUST NOT write crop files using bare filenames such as `img-001.png` without prefixing the resolved output directory.
- After each crop write, the microagent MUST verify that the written file path is inside the resolved `crop_output_dir`.
- If the microagent cannot resolve or verify the target directory safely, it MUST skip crop persistence, keep analysis in-memory when possible, and record an `open_question` explaining that crop persistence was disabled due to an unsafe path configuration.

### Non-negotiable rule (prevents 100% needs-review runs)
If `candidates` are not provided, the agent MUST discover candidates from the **live DOM** using Playwright. Only fall back to `needs-review` when the element cannot be located or cannot be cropped (detached/hidden).

### Candidate Discovery (when `candidates` not provided)
Evaluate, at minimum:
- `<img>` elements
- inline `<svg>` elements that are intended as images (e.g., `role="img"`, `aria-label`, `aria-labelledby`)
- any element with `role="img"`

Do not rely on HTML alone: this microagent MUST attempt to obtain the **actual visual content** of each candidate by capturing a rendered crop (see Image Acquisition below).

After discovery, normalize the candidate list into a deterministic order before sampling. Prefer a stable DOM-order selection so the same page tends to yield the same 12 reviewed items across reruns.

Canonical sampling guardrails:
- Freeze the sampled 12 candidates before capturing crops.
- Use the same frozen sample for crop capture, accessible-name computation, and final JSON serialization.
- If the page mutates after sampling, retry element lookup against the frozen identity only. Never rebuild the sample mid-run unless the whole run is restarted and the restart is recorded as a limitation.

---

## Image Acquisition (required behavior)
For each candidate, obtain an image representation to analyze.

This microagent is **Playwright-first**: it uses the live page to acquire crops and does not require pre-saved HTML/screenshot artifacts.

### Preferred: rendered element crop (Playwright)
When Playwright access is available, capture a per-element screenshot crop using the element handle bounding box / screenshot APIs. This is the most reliable method because it matches what the user sees.

Implementation guidance (basic, reliable, low-cost):
1) Use a stable selector for each candidate (CSS selector preferred).
2) Acquire crop using Playwright locator APIs:
  - `locator = page.locator(selector).first()`
  - `await locator.scrollIntoViewIfNeeded()`
  - `await locator.screenshot({ path })`
3) Save crops to `crop_output_dir` using deterministic filenames (e.g., `img-001.png`).
   - Build `path` by joining the resolved `crop_output_dir` with the deterministic filename.
   - Do not pass a cwd-relative path to Playwright when the caller expects canonical audit artifacts.
4) If the element is detached/not visible, retry once after 250–500ms. If it still fails, use the fallbacks below.

Selector stability rule:
- The persisted `selector` field SHOULD use the highest-stability locator that still resolves the frozen candidate.
- If only a positional selector would resolve after reflow, keep the original stable identity in the output and set `verdict="needs-review"` unless nearby evidence proves the node is unchanged.

### Navigation behavior
- If `page_url` is provided and current URL differs, the agent SHOULD navigate to `page_url`.
- The agent should wait cheaply for stability: `domcontentloaded` + 250–500ms.

Authentication guardrail:
- The agent MUST NOT guess credentials.
- If navigation is blocked by auth/consent walls and crops cannot be obtained, record an `open_question` and mark affected items as `needs-review`.

### Special cases
- `data:` URLs: do not attempt to decode large base64 payloads; prefer rendered crop.
- CSS `background-image`: only treat as a candidate when the element is exposed as an image to AT (e.g., `role="img"` or meaningful accessible name); otherwise assume decorative.

---

## Output (strict JSON)
Return ONLY JSON in this shape:

```json
{
  "image_alt_reviews": [
    {
      "id": "img-001",
      "selector": "...",
      "element_type": "img|svg|role-img",
      "image_source": {
        "resolved_url": "...",
        "acquisition": "download|rendered-crop|fullpage-fallback|unavailable",
        "download": {
          "attempted": true,
          "status": "ok|blocked|failed|skipped",
          "http_status": 200,
          "mime": "image/png",
          "bytes": 12345
        }
      },
      "accessible_name": {
        "computed": "...",
        "source": "alt|aria-label|aria-labelledby|title|none"
      },
      "verdict": "pass|fail|needs-review",
      "wcag": ["1.1.1"],
      "visual_summary": "short neutral description of what the image appears to depict (best-effort)",
      "evidence": "short explanation grounded in what is visible in the acquired image (download/crop) and/or nearby DOM context",
      "problems": [
        "missing-alt",
        "generic-alt",
        "mismatch-alt",
        "filename-alt",
        "redundant-with-nearby-text",
        "decorative-should-be-empty",
        "image-of-text"
      ],
      "suggested_fix": {
        "type": "html",
        "patch_hint": "precise change, e.g. add alt=\"...\" or aria-label=\"...\"; if decorative: alt=\"\" and ensure not focusable",
        "confidence": 0.0
      }
    }
  ],
  "summary": {
    "total": 0,
    "pass": 0,
    "fail": 0,
    "needs_review": 0
  },
  "open_questions": [
    "Any item that cannot be validated without product context (e.g., brand logo meaning)"
  ]
}
```

Notes:
- `confidence` MUST be in range [0, 1].
- If the agent cannot confidently describe the image, it should:
  - set `verdict="needs-review"`
  - keep `patch_hint` generic (or omit proposed wording if `do_not_suggest_new_copy=true`)
  - set `image_source.acquisition` to the fallback actually used

Additional requirement:
- The agent MUST populate `image_source.acquisition` truthfully (`rendered-crop` when a per-element screenshot was used, `download` when downloaded bytes were analyzed, `fullpage-fallback` when only a full screenshot was available).

## Stable Output Artifact
When the caller provides an audit artifact directory, this microagent SHOULD also persist its structured result as a stable JSON artifact named:

- `alt-text-review.json`

Persistence rules:
- The canonical path SHOULD be `artifacts/a11y/<target-slug>/alt-text-review.json`.
- If the caller already provides a more specific artifact directory, the microagent SHOULD write `alt-text-review.json` inside that resolved directory.
- If the caller provides `constraints.crop_output_dir` but no explicit artifact directory, the microagent SHOULD derive the audit artifact root from that crop directory and write the stable `alt-text-review.json` there when possible.
- The persisted file MUST contain the same structured payload returned by this microagent, optionally wrapped with minimal execution metadata.

Recommended persisted shape:

```json
{
  "status": "completed",
  "tool": "alt_text_validator",
  "targetUrl": "https://example.com/page",
  "generatedAt": "2026-04-24T12:34:56Z",
  "image_alt_reviews": [],
  "summary": {
    "total": 0,
    "pass": 0,
    "fail": 0,
    "needs_review": 0
  },
  "open_questions": []
}
```

Rules:
- `image_alt_reviews`, `summary`, and `open_questions` remain the source-of-truth payload.
- Additional metadata such as `status`, `tool`, `targetUrl`, and `generatedAt` is allowed, but it MUST NOT change the meaning of the returned review data.
- This file is a specialized supporting artifact for image alternative text validation only.
- This file MUST NOT be treated as a replacement for `semantic-before.json` or `semantic-after.json`.
- The parent `accessibility_agent` MAY use this file as traceable evidence input when consolidating `semantic_issues[]`.

---

## Validation Rules (behavior)
### Lightweight visual analysis protocol (required)
Use the rendered crop (when available) to produce a **minimal** `visual_summary` and determine whether the accessible name matches.

Rules:
- `visual_summary` MUST be <= 12 words and neutral.
- `evidence` MUST be 1–2 short sentences, explicitly tying the accessible name to what is visible.
- Mention at most **one** salient attribute (e.g., shirt color) **only if** it materially supports match/mismatch.
- If the crop is obscured/too small/blurred (cookie banner overlay, carousel partially offscreen), set `verdict="needs-review"` and explain why.

### What “good” looks like
- Alternative text communicates the **purpose** of the image in context.
- Avoid starting with “image of / picture of”.
- Avoid filenames, hash strings, or CSS class names.
- If the image is purely decorative, prefer `alt=""` (and ensure it is not focusable or announced).
- If the image is functional (button/link), its accessible name must reflect the action (may be better on the button/link than on the image).
- If the image contains text (image-of-text), the alt should include that text (or the essential part), unless it’s decorative.

### How to detect mismatch (core responsibility)
Compare the **acquired visual content** against the computed accessible name:
- If the accessible name describes a different object/action than what is visible, flag `mismatch-alt`.
- If the accessible name is too generic relative to the content (e.g., "image"/"logo" without context), flag `generic-alt` (or `needs-review` if branding meaning is ambiguous).
- If the image is purely decorative (borders, flourishes, repeated background patterns) and has a non-empty accessible name, flag `decorative-should-be-empty`.

Determinism guardrail:
- Do not emit a `fail` verdict for a candidate whose crop, selector rematch, or nearby context is unstable across the current run.
- When acquisition instability prevents confident comparison, prefer `needs-review` with explicit evidence about the instability rather than promoting a speculative `fail`.

### Minimal/safe suggestions
- Prefer editing existing `alt` over adding new ARIA unless necessary.
- Prefer `alt` for `<img>`.
- Prefer `aria-label` only when there is no better native attribute.
- Ensure any `aria-labelledby` references a real id.

### Non-invention guardrail
- Do not invent product-specific meaning.
- For logos/brands, suggest neutral alternatives (e.g., "Logo da empresa") unless the brand name is clearly present in nearby text.

---

## Integration Contract (caller expectations)
When invoked by `accessibility_agent`, the caller should:
1) Always pass `page_url` for the live page under review.
2) Optionally pass `candidates` (selectors from axe nodes) to improve targeting, but do not rely on candidates alone.
3) Optionally pass `constraints.crop_output_dir` so crops are saved under the caller's artifact folder.
  - When the caller expects files on disk, it SHOULD pass an absolute workspace path, not a repo-relative path.
4) Treat `fail` items as semantic issues that can generate patches (HTML attribute updates).
5) Include `needs-review` items in `limitations.md` if they require human confirmation.
6) Treat this microagent as a structured-data validator. Do not require it to write a canonical Markdown report unless its contract is explicitly extended to do so.
