---
fidelity: [discovery, exploration]
artifact: [story-map]
format: md
example-of: none
---

# Story Map — Context Setup (sketch)

**Sources / context:**
`abd-skills/practices/context-driven-delivery/skills/abd-context-{app-extractor,app-sandbox,to-markdown,semantic-index,chunk,db-embed,db-ask}/SKILL.md`;
`abd-context-driven-delivery/primitives/.context/module-context.md`;
`abd-context-driven-delivery/primitives/tools/.context/module-context.md`;
`abd-context-driven-delivery/primitives/actions/.context/module-context.md`;
`abd-context-driven-delivery/context_tools/.context/module-context.md` (contrast — deliberately **not** that pattern);
`abd-context-driven-delivery/utilities/echo`, `utilities/agent_skills` (precedent — plain `@action`/`@tool` toolsets, not `@context`).

**Framing decision (confirmed — see [`0001-plain-toolset-not-context-domain`](../../cdr/0001-plain-toolset-not-context-domain.md)):** Today these seven capabilities are independent script-based skills. We are re-platforming them as **one agentic toolset** built directly on `primitives` (`@agentic_toolset` + `@tool` + `@action`) — *not* a `context_tools` `@context` domain, because there is no generate/validate/satisfy rubric here; there is a pipeline of deterministic steps interleaved with AI-judgment checkpoints.

---

## Actors in this map

- **User** — decides which capture path to use; initiates each sub-epic
- **AI Chat** — reads an `@action`'s expanded instructions; decides which tool to call next; owns every judgment checkpoint (no tool, no observable script output)
- **Tool** — the plain Python method that runs a real script and returns a deterministic result

`Actor --> Story` keeps the Stories notation. There is no AI-routing story between paths — the User's intent selects the entry-point sub-epic directly.

---

(E) Set Up Context Memory
    * approx 20-24 total stories
    (E) Capture From Documents                   // Increment 1 — User-chosen capture path
        (S) User --> Capture From Documents
            source-folder-capture-begins
                given a Source Folder of office documents at folder.path
                when the User requests capture from that Folder
                then the AI Chat calls Convert To Markdown with the Source Folder path
        (S) Tool --> Convert To Markdown
            documents-converted-file-by-file
                given a Source Folder path
                when convert_to_markdown(folder.path) is called
                then each office file is converted to a Markdown Document at document.path
                    and Structure Notes are produced alongside it
        (S) AI Chat --> Review Document Structure
            structure-accepted-tagging-begins
                given a Markdown Document and Structure Notes from Convert To Markdown
                when the AI Chat reads the Structure Notes
                then the AI Chat calls Tag Content By View with the accepted Markdown Document
            structure-flagged-triggers-semantic-repass
                given a Markdown Document whose Structure Notes show flat or missing headings
                when the AI Chat reads the Structure Notes
                then the AI Chat requests a semantic re-pass of the Markdown Document
                    and Tag Content By View is not called until the re-pass returns
        * approx 1-2 more stories (multi-file error handling, partial-conversion recovery)
    (E) Capture From Live App                    // Increment 2 — User-chosen capture path, deferred
        (S) User --> Capture From Live App
        (S) Tool --> Stub External Dependencies
        (S) Tool --> Capture App Pages
        (S) AI Chat --> Review Capture Coverage
        * approx 2-3 more stories (human approval gate, reasonableness review, retry on incomplete capture)
    (E) Prepare Content For Retrieval
        (S) Tool --> Tag Content By View
            content-tagged-by-view
                given a Markdown Document at document.path
                when semantic_index(document.path) is called
                then each piece is tagged by view (story, domain, architecture, ux)
                    and a Coverage Report is returned alongside the Tagged Chunks
        (S) Tool --> Draft Chunking Spec
            spec-drafted-with-structural-scan
                given Tagged Chunks and a Markdown Document at document.path
                when draft_chunking_spec(document.path) is called
                then a structural scan report is produced showing heading and table metrics
                    and a Chunking Spec YAML is written at memory.path/context_chunking_spec.yaml
        (S) AI Chat --> Review Chunking Spec
            spec-accepted-chunking-begins
                given a Chunking Spec YAML and a structural scan report
                when the AI Chat reviews the spec boundaries and heading metrics
                then the AI Chat calls Apply Chunking Spec with the accepted spec
            spec-edited-before-chunking
                given a Chunking Spec where boundaries or taxonomy look wrong for the document shape
                when the AI Chat reviews the spec
                then the AI Chat edits the YAML and calls Apply Chunking Spec with the revised spec
        (S) Tool --> Apply Chunking Spec
            chunks-produced-from-spec
                given a Chunking Spec at memory.path/context_chunking_spec.yaml
                when chunk_markdown(document.path, spec.path) is called
                then Chunks are produced under memory.path/
                    and a Chunk Count is returned
            chunk-count-anomaly-triggers-spec-edit
                given a Chunk Count that looks like one giant chunk relative to document shape
                when the AI Chat reviews the Chunk Count
                then the AI Chat edits the Chunking Spec and re-calls Apply Chunking Spec
        (S) Tool --> Embed Chunks
            chunks-embedded-into-faiss-index
                given a Memory Path with a reasonable Chunk Count
                when embed_chunks(memory.path) is called
                then a FAISS Index is written at index.path
                    and the Index Path is returned
        (S) AI Chat --> Confirm Memory Ready
            memory-ready-reported-to-user
                given an Index Path from Embed Chunks
                when the AI Chat finishes the preparation pipeline
                then the AI Chat reports memory is ready under memory.path/rag/
    (E) Answer From Memory
        (S) User --> Ask From Memory
            question-routed-to-search
                given a ready FAISS Index under memory.path/rag/
                when the User asks a question about captured content
                then the AI Chat derives a Query from the User's words
                    and calls Search Memory
        (S) Tool --> Search Memory
            memory-searched-returns-ranked-chunks
                given a Query derived from the User's question and an Index Path
                when search_memory(query, index.path) is called
                then a ranked list of Chunks and Scores is returned from the FAISS Index
        (S) AI Chat --> Answer With Citations
            answer-composed-with-source-citations
                given ranked Chunks and Scores from Search Memory
                when the AI Chat reads each Chunk's chunk_type front matter to weight results
                then an Answer is composed that cites source.path and section per Chunk used
        * approx 1-2 more stories (empty-index fallback, multi-corpus query)

---

## Scope boundary

**In scope (this toolset):** everything currently split across the 7 skills — capturing a live app (sandbox + extractor) *or* converting documents, tagging by view, chunking, embedding, and querying.

**Out of scope:** the CDD practice itself (stories/bdd/clean-engineering) — this toolset produces *memory*, other toolsets consume it. No new capture surfaces beyond what the 7 skills already support.

**Confirmed 2026-08-04:** Increment 1 = documents-only (`Capture From Documents` → `Prepare Content For Retrieval` → `Answer From Memory`). Live-app capture (`Capture From Live App`) is Increment 2, deferred. See [`0001-plain-toolset-not-context-domain`](../../cdr/0001-plain-toolset-not-context-domain.md) for the single-toolset rationale.

---

## Thin slices

### Increment 1: `Ask a question, get a cited answer, from a folder of documents`

**Outcome:** Point the toolset at a folder of office documents; get back a queryable memory you can ask questions against with citations.

**Stories in this increment** *(flow order)*:
- User --> Capture From Documents
- Tool --> Convert To Markdown
- AI Chat --> Review Document Structure
- Tool --> Tag Content By View
- Tool --> Draft Chunking Spec
- AI Chat --> Review Chunking Spec
- Tool --> Apply Chunking Spec
- Tool --> Embed Chunks
- AI Chat --> Confirm Memory Ready
- User --> Ask From Memory
- Tool --> Search Memory
- AI Chat --> Answer With Citations

### Increment 2: `Capture a live application instead of documents`

**Outcome:** Same preparation and answer pipeline, but the entry point is a live app — User chooses `Capture From Live App`.

**Slicing notes:** `Stub External Dependencies` and `Capture App Pages` are each multi-step, judgment-heavy flows. Candidates for `mode="tool"` deferral (called actions, not inlined recipes) — flagged as `?` pending the BDD/Clean-Engineering pass.

**Stories in this increment:**
- User --> Capture From Live App
- Tool --> Stub External Dependencies
- Tool --> Capture App Pages
- AI Chat --> Review Capture Coverage
- *(rejoins Prepare Content For Retrieval / Answer From Memory unchanged)*

* approx 2-4 more stories once BDD detail surfaces edge cases

---

## What to notice about the actor model

- The **User** decides the capture path — documents or live app. Each path is its own sub-epic with its own entry story. There is no routing story between them.
- Every **Tool** call is real Python executing a real script — deterministic, testable in isolation.
- **AI Chat** stories own every judgment checkpoint: structure quality, chunk-count sanity, citation weighting. These have no tool and are why this is `@action`, not a plain pipeline.

---

## Resolved this pass

- **Capture paths are separate epics, User-initiated.** `AI Chat --> Choose Capture Path` and `Action --> Orchestrate Capture` removed. Each path is its own sub-epic with distinct stories.
- **Story-level tool boundary for the preparation stage.** `Run Preparation Step (×3)` split into `Tag Content By View`, `Draft Chunking Spec`, `Review Chunking Spec`, `Apply Chunking Spec`, `Embed Chunks` per `branch-on-mechanical-uniqueness`. Confirmed against `abd-context-chunk/SKILL.md` (two distinct scripts; explicit strategy-pass vs straight-through judgment step).
- **User story then-clause.** `User --> Capture From Documents` now shows the AI Chat calling Convert To Markdown — not the tool's output, which belongs to the Tool story.
- **"Ask" independence from "setup."** Confirmed against `abd-context-db-ask/SKILL.md` line 37: path-addressed, no stored session dependency.
- **Package location.** Confirmed: `utilities/context_setup/` — matches `echo`/`agent_skills` plain-toolset precedent.

## Unresolved / flagged for next pass

- `?` Which stages in `Capture From Live App` get `mode="tool"` deferral vs stay inlined — flagged for BDD/Clean-Engineering pass when Increment 2 activates.
