# Skill errors log — abd-architecture-specification

### Code and test examples hard-coded to abd-clean-code / abd-story-acceptance-test

- **Context:** YAML description, Agent Instructions step 4, Build step 4, Validate checklist, rule `code-examples-follow-project-coding-and-testing-standards.md`
- **DO / DO NOT:** Walkthrough code samples must follow the **project's coding standard** and test snippets must follow the **project's testing standard** — *whichever the project has agreed*. `abd-clean-code` and `abd-story-acceptance-test` are the defaults when in scope, not universal hard requirements. Do **not** say "code examples come from the abd-clean-code and ATDD skills" as if no other standard could possibly apply.
- **Example (wrong):** YAML description originally said: "Use this skill when you have a layered architecture from abd-architecture-description and a list of mechanisms from abd-architecture-mechanisms" — treated the two skills as required input sources.
- **Example (correct):** YAML description now says: "Use this skill when you have a layered architecture description and a list of mechanisms with intent" — source-agnostic; conditional references say "defaulting to abd-clean-code when it is in scope" and "defaulting to abd-story-acceptance-test when it is in scope".
- **Likely source:** prompt gap
- **Status:** confirmed

---

### External dependency on mern-technical-architecture

- **Context:** Agent Instructions step 1 in SKILL.md
- **DO / DO NOT:** The skill must be self-contained. Worked examples for tone/shape calibration live **inside this skill** in the template's illustrative-example block — not as a relative link to a sibling skill's input files. Pointing at a sibling skill creates a hard dependency that breaks when this skill is deployed elsewhere.
- **Example (wrong):** Agent Instructions step 1 originally ended with: "The closest worked example of the reference document this skill produces is **`mern-architecture.md`**(../mern-technical-architecture/inputs/mern-architecture.md) — read it before generating new sections so the shape stays consistent."
- **Example (correct):** "For shape and tone, the filled illustrative example block at the bottom of `templates/architecture-specification.md` is a worked example of what one mechanism section should look like when complete. Read it once before generating new sections." — example lives inside the skill. Current SKILL.md has this correct text.
- **Likely source:** prompt gap
- **Status:** confirmed

---

### Instructions named specific skills to read, not what information to gather

- **Context:** Agent Instructions step 1, Build steps 1—2, Core concepts "Mechanism" and "Layered description vs. mechanism reference" sections, rule `grounded-in-architecture-description-and-mechanisms.md`
- **DO / DO NOT:** When an instruction step needs information, describe **what information** the agent must have in front of it, not **which sibling skill produces it**. Sibling skills may be mentioned as one possible source — not as required inputs.
- **Example (wrong):** Core concepts said "Mechanisms come from the **abd-architecture-mechanisms** output." and "**abd-architecture-description** answers *what are the layers and what tech sits in each*." — frames the work as fetching from specific skills.
- **Example (correct):** Core concepts now says "Mechanisms come from whatever the team uses as its architecture source of truth — an ADR, a wiki page, a decision document, or a sibling skill's output." and "The **layered description** answers *what are the layers and what tech sits in each*." Also the YAML description now says "layered architecture description and a list of mechanisms with intent" without naming specific skills.
- **Likely source:** prompt gap
- **Status:** confirmed

---

### Rule "grounded-in" named specific skills as required vocabulary source

- **Context:** `rules/grounded-in-architecture-description-and-mechanisms.md`
- **DO / DO NOT:** The rule that checks vocabulary consistency should refer to the "architecture's source of truth" — whatever form that takes — not mandate that layers/mechanisms come specifically from abd-architecture-description or abd-architecture-mechanisms. Those skills are one possible source.
- **Example (wrong):** Rule title was "Reference is grounded in abd-architecture-description and abd-architecture-mechanisms"; content required layers to match "the output of abd-architecture-description" and mechanisms to match "the output of abd-architecture-mechanisms".
- **Example (correct):** Rule renamed to `grounded-in-architecture-source-of-truth.md`, title is "Reference is grounded in the architecture's source of truth". Content says layers and mechanism names must match "the agreed source of truth for the same architecture — whatever form that takes (an ADR, a wiki page, a decision document, a sibling skill's output, or any other agreed record)." SKILL.md rebundled from updated `rules/*.md`.
- **Likely source:** prompt gap
- **Status:** confirmed

---

### Template and example text referenced specific sibling skills as required sources

- **Context:** `templates/architecture-specification.md` — Sources line, Architecture Layers comment, References section; illustrative example block in SKILL.md
- **DO / DO NOT:** Template placeholders and comments must tell the practitioner to cite **whatever source they used**, not to copy from specific skill outputs. Sibling skills may be mentioned as one example option.
- **Example (wrong):** Template had `> Sources: layers from **abd-architecture-description**; mechanisms list from **abd-architecture-mechanisms**.` and `<!-- Paste / summarize the layer block from abd-architecture-description verbatim. -->` and References listed `output of **abd-architecture-description**` and `output of **abd-architecture-mechanisms**` as if those skills were always the source.
- **Example (correct):** Template now has `> Sources: [cite the architecture's source of truth — ADR, wiki, decision doc, or sibling-skill output]; mechanisms from [cite source].` and the comment says `<!-- Paste / summarize the layer block from the architecture's agreed source of truth (ADR, wiki, decision doc, or sibling skill). -->` References now show bracketed placeholders with sibling skills listed as optional examples.
- **Likely source:** prompt gap
- **Status:** confirmed

---

### "When to use" described reference as locking an artifact list, not design+implementation guidance

- **Context:** `When to use this skill` section — second bullet
- **DO / DO NOT:** When summarising what the reference captures, say it locks **both the design and implementation constraints / guidance**. Do **not** enumerate the artifacts (principles, patterns, file layout, diagrams, etc.); the user-facing value is the two-sided contract.
- **Example (wrong):** "you want to **lock the principles, patterns, and file layout** before any production code is written." — lists artifacts; reader must infer the two-sided contract.
- **Example (correct):** "you want to **lock both the design and implementation constraints / guidance** before any production code is written." — current SKILL.md has this exact corrected text.
- **Likely source:** unclear expectation
- **Status:** confirmed

---

### "When to use" bullets described inter-skill pipeline plumbing

- **Context:** `When to use this skill` section
- **DO / DO NOT:** `When to use` bullets must describe **situations a practitioner actually faces**, not pipeline plumbing like "you have output from skill X and want to feed it into skill Y".
- **Example (wrong):** Earlier draft opened with bullets: "You have an architecture layer description (from **abd-architecture-description**) and a list of mechanisms (from **abd-architecture-mechanisms**) and you need to turn them into one reviewable document." and "You are about to run **abd-build-architecture-skill** and need the reference doc it consumes to exist first."
- **Example (correct):** Current `When to use` section has six bullets that all describe real practitioner situations: drift in codebase, new architecture adoption, onboarding pain, recurring review comments, etc. No sibling-skill names appear.
- **Likely source:** prompt gap
- **Status:** confirmed
