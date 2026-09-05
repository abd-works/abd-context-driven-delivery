# abd-ux-specification — corrections log

Log entries follow the workspace `correct-output` rule format. Each entry stays attached to the skill that produced the wrong output, not to chat history.

---

## Entry 1 — production implementation → clickable prototype

- **Context:** `SKILL.md` / `reference/concepts.md` described `abd-interface-design` as production-grade framework code with AC tests and host lint gates.
- **DO / DO NOT:** **DO** position this skill as a **clickable hi-fi prototype** — real HTML/CSS/JS look-and-feel, stubbed or faked domain logic, AC demonstrated via click paths. **DO NOT** describe output as production implementation, full domain behaviour, or per-AC automated test suites.
- **Example (wrong):** "Translate approved hi-fi mockups into production-grade, accessible interface code" with lint gates, type-check, and one test per AC clause.
- **Example (correct):** Runnable prototype files plus `ux-specification.md` with a stub catalogue; stakeholders click through flows; major logic uses fixtures and fakes.
- **Likely source:** `unclear expectation` — skill folder renamed to `abd-ux-specification` while body still reflected interface implementation.
- **Status:** confirmed

---

## Entry 2 — missing brand-assets gate before hi-fi styling

- **Context:** `SKILL.md` generation flow jumped from inputs to CSS without asking about logos, colour scheme, or whether to create provisional stand-ins.
- **DO / DO NOT:** **DO** search the host project for brand assets, ask the key questions in `reference/brand-assets-questionnaire.md` when gaps exist, offer to create documented provisional stand-ins, and record decisions in `ux-specification.md`. **DO NOT** ship unstyled prototypes or invent brand without asking when no authoritative brand pack exists.
- **Example (wrong):** Agent builds grey-box HTML tables with system font and no logo because brand was never discussed.
- **Example (correct):** Agent asks colour scheme / logo / photography questions, creates `prototype/assets/logo.svg` with user approval, documents tokens and provisional assets in **Brand assets** section per `templates/brand-assets-brief.md`.
- **Likely source:** `prompt gap`
- **Status:** confirmed

---

## Entry 3 — brand questionnaire must use AskQuestion tool

- **Context:** `reference/brand-assets-questionnaire.md` section 2 said "Present these in chat" for ten numbered questions.
- **DO / DO NOT:** **DO** run section 2 steps A–F via the **`AskQuestion` tool**; use chat only for `other` follow-ups (paths, hex, brand name). **DO NOT** dump the questionnaire as a numbered list in chat or proceed without tool responses.
- **Example (wrong):** Agent posts all ten brand questions as markdown bullets and starts building CSS in the same turn.
- **Example (correct):** Agent calls `AskQuestion` for `colour-scheme` with domain-aligned palette options; waits for selection; then calls `AskQuestion` for `logo`; records option ids in **Brand assets** brief.
- **Likely source:** `prompt gap`
- **Status:** confirmed

---

## Entry 4 — ux-specification.html must iframe prototype index

- **Context:** Deliverable listed only `ux-specification.md` and raw `prototype/index.html`; no framed spec review page; catalog skill hero ignored `reference/example/` HTML folders.
- **DO / DO NOT:** **DO** author `ux-specification.html` from `templates/ux-specification.html` with iframe `src` → `prototype/index.html` (or `example/index.html`); embed `reference/example/index.html` on the Foundry skill page when present. **DO NOT** commit only a Markdown link to the prototype when HTML exists in the deliverable folder.
- **Example (wrong):** Reviewers must open `prototype/index.html` separately; skill catalog page shows empty hero despite `reference/example/index.html`.
- **Example (correct):** `ux-specification.html` frames `prototype/index.html`; Foundry `abd-ux-specification.html` hero shows clickable PawPlace prototype in iframe.
- **Likely source:** `prompt gap`
- **Status:** confirmed
