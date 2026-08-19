---
fidelity: [discovery]
artifact: [story-map]
format: md
---

# Story Map — Context Setup

**Sources / context:**
`abd-skills/practices/context-driven-delivery/skills/abd-context-{app-extractor,app-sandbox,to-markdown,semantic-index,chunk,db-embed,db-ask}/SKILL.md`;
`utilities/context_setup/.context/cdr/0001-plain-toolset-not-context-domain.md`;
`utilities/context_setup/.context/sessions/context-setup/context-setup-sketch.md`;
`utilities/context_setup/.context/sessions/context-setup/grill-answers.md`

---

(E) Set Up Context Memory
    (E) Capture From Documents
        (S) User --> Capture From Documents
        (S) Tool --> Convert To Markdown
        (S) AI Chat --> Review Document Structure
        * approx 3-5 more stories (multi-file error handling, approval gate, retry)
    (E) Prepare Content For Retrieval
        (S) Tool --> Tag Content By View
        (S) Tool --> Draft Chunking Spec
        (S) AI Chat --> Review Chunking Spec
        (S) Tool --> Apply Chunking Spec
        (S) Tool --> Embed Chunks
        (S) AI Chat --> Confirm Memory Ready
    (E) Answer From Memory
        (S) User --> Ask From Memory
        (S) Tool --> Search Memory
        (S) AI Chat --> Answer With Citations
        * approx 1-2 more stories (empty-index fallback, multi-corpus query)
    (E) Capture From Live App
        (S) User --> Capture From Live App
        (E) Stub External Dependencies
            (S) AI Chat --> Classify External Dependencies
            (S) Tool --> Write External Stubs
            (S) Tool --> Smoke Test App
        (E) Capture App Pages
            (S) Tool --> Scout App Pages
            (S) AI Chat --> Review Capture Coverage
            (S) Tool --> Complete App Capture
            * approx 1-2 more stories (multi-surface hybrid)

---

## Scope boundary

**In scope:** capturing a live app (sandbox + extractor) or converting documents; tagging by view; chunking; embedding; querying. Replaces the 7 separate script-based abd-context-* skills with one agentic toolset built on primitives.

**Out of scope:** the CDD practice itself (stories/bdd/clean-engineering) — this toolset produces memory, other toolsets consume it. No new capture surfaces beyond what the 7 skills already support.

---

## Thin slices

### Increment 1: Ask a question, get a cited answer, from a folder of documents

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

### Increment 2: Capture a live application instead of documents

**Outcome:** Same preparation and answer pipeline, but the entry point is a live app — User chooses Capture From Live App.

**Stories in this increment** *(flow order)*:
- User --> Capture From Live App
- AI Chat --> Classify External Dependencies
- Tool --> Write External Stubs
- Tool --> Smoke Test App
- Tool --> Scout App Pages
- AI Chat --> Review Capture Coverage
- Tool --> Complete App Capture
- *(rejoins Prepare Content For Retrieval / Answer From Memory unchanged)*
