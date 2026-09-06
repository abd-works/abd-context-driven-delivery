# Rule: UX specification page embeds the prototype index when HTML exists

**Scanner:** AI review

When a prototype folder contains runnable HTML, reviewers need one page that pairs the spec with a live preview. The **`ux-specification.html`** companion frames the prototype **`index.html`** entry; the Markdown spec remains the source of truth for stubs and AC paths.

## DO

- **Detect prototype HTML** — look for `prototype/index.html`, `reference/example/index.html`, or the first `*.html` in an `example/` folder beside the spec.

  **Example (pass):** `docs/increments/2-click-and-collect/specification/prototype/index.html` exists; agent authors `ux-specification.html` in the same `specification/` folder.

- **Point the iframe at the index entry** — `src` is relative to `ux-specification.html` (typically `prototype/index.html`).

  **Example (pass):** `<iframe src="prototype/index.html" title="Click-and-collect prototype">` on the spec page; header link opens the same path in a new tab.

- **Ship `ux-specification.html` from `templates/ux-specification.html`** — replace `{{SCOPE_NAME}}` and `{{PROTOTYPE_INDEX}}`; keep `ux-specification.md` link in the header.

  **Example (pass):** `specification/ux-specification.html` and `specification/ux-specification.md` sit together; Metadata table in the Markdown lists both paths.

- **Record both paths in `ux-specification.md` metadata** — prototype entry and HTML spec preview page.

  **Example (pass):** `| Spec preview (iframe) | specification/ux-specification.html |`

## DO NOT

- **Link only to raw `index.html` in Markdown** when the deliverable folder has HTML and no `ux-specification.html` companion exists.

  **Example (fail):** `ux-specification.md` says "open prototype/index.html" but there is no framed spec page for stakeholders who expect a single review URL.

- **Iframe a non-index HTML file** when `index.html` exists in the same folder.

  **Example (fail):** iframe `prototype/checkout.html` while `prototype/index.html` is the wired entry with full navigation.

- **Use absolute URLs** to a localhost server in committed artifacts — use relative paths; document that a static server may be needed in the frame note.

  **Example (fail):** `src="http://localhost:8765/index.html"` hard-coded in committed `ux-specification.html`.
