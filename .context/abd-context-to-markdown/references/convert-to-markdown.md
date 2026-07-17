# Convert to Markdown (core converter + post-process + quality loop)

This page is the **convert** step in the full pipeline. The **whole chain** (convert → assess structure → spec → chunk → embed, flags, strategy pass) lives in **[process.md](../process.md)**—read that for order and commands.

**Principle:** **Structural composition and decomposition**—chapters, sections, tables you can split on—belong in **conversion and markdown post-process** (`pdf_markdown_post`, corpus scripts). The **chunker** only cuts along boundaries already present in the files; it does not rebuild hierarchy. See [chunking-spec.md](chunking-spec.md) (*Chunker vs converter*).

---

## What happens on disk

1. **Core markdown converter** — `convert_to_markdown.py` uses MarkItDown (and format-specific paths for Office XML, PPTX charts, etc.) to turn each supported source into a `.md` file under **`markdown/`**, mirroring paths and names. Details: [output.md](output.md).

2. **Built-in post-processors** — After extraction, **PDFs** (and only PDFs in the default tool) pass through shared cleanup in `pdf_markdown_post` (banner collapse, conservative `CHAPTER` / `APPENDIX` / `PART` line promotion, optional outline alignment when **PyMuPDF** is installed). That is **not** guaranteed to fix every book; it is generic. Deep dive: [pdf-extraction-advanced.md](pdf-extraction-advanced.md).

---

## After convert: assess headings and subheadings

**Goal:** Chunking and RAG work best when the markdown has real **sections** (headings), not a flat wall of text.

**Agents and humans should check:**

- Does the file have **`#` / `##` / `###`** (or enough structure) where the source had chapters or sections?
- Run or inspect **`draft_chunking_spec.py`** output (or open **`markdown/structural_scan_report.txt`**) — it reports heading counts and hints (e.g. chapter-like patterns vs noise).

**If structure looks bad** (few or no headings, wrong breaks, no subsections where you expect them):

1. **Tell the user clearly** what failed (e.g. “almost no `##`, chunking will be poor”).
2. **Suggest a fix path:**
   - **Turn on or add** something that already exists: e.g. install **PyMuPDF** for PDF outline injection, adjust env flags (`PDF_SKIP_*`) documented in [pdf-extraction-advanced.md](pdf-extraction-advanced.md), or re-export the source with better tags.
   - **Or** add a **bespoke post-processor** — a script under **`<topic_root>/scripts/post-processors`** that rewrites `markdown/*.md` for *this* corpus and potentially other of te same type (see below).

3. **Implement, run, repeat:** Add or change the bespoke script, run it on `markdown/`, re-check headings (and re-run structural scan if needed). **Repeat** until structure is good enough to chunk, or until you hit a limit and need a human decision.

**Choosing “which post-processor”:** The **agent** should pick the most likely improvement when the default pipeline is not enough—e.g. outline pass if the PDF has bookmarks; regex or scripted fixes if the problem is a known pattern; **not** one-size-fits-all hacks in the shared skill for a single publisher.

---

## Last resort: the source is still a mess (semantic / topic pass)

Sometimes the extract stays **unusable for heading-based chunking**: one long stream of text, headings missing or wrong, or topics **mixed in one block**. Regex and bespoke layout fixes are not enough.

**Then run an AI-led semantic pass** (not a fixed script in the skill—**judgment** in chat or a corpus-specific tool you control):

1. **Read** the markdown in meaningful slices (or the whole file if size allows).
2. **Decide what belongs together** — which sentences and paragraphs form one **topic**; whether a topic should split into **sub-topics**.
3. **Materialize structure** — e.g. inject `##` / `###` titles that match *meaning*, add blank-line breaks between units, or write a **cleaner parallel file** under `markdown/` (keep a backup of the raw extract).
4. **Complete one full pass**, then **look at the results again**: coherence, missing boundaries, wrong merges. **Iterate** until sections reflect topics well enough to draft a spec and chunk.

Only after this should you rely on `draft_chunking_spec.py` and heading-driven splits. For taxonomy and chunk labels after semantic restructuring, see [chunking-spec.md](chunking-spec.md).

---

## Bespoke post-processors (corpus scripts)

Shared skill code stays generic. Anything **book- or publisher-specific** belongs in:

**`<topic_root>/scripts/`** — same folder as `markdown/` and `memory/` (the chunking spec lives **inside** `memory/context_chunking_spec.yaml`).

Name scripts clearly (`prepare_handbook_headings.py`, …), document usage in the script docstring, and optionally point to them from comments in `context_chunking_spec.yaml`. More convention: [process.md](../process.md) (section *Corpus preprocess scripts*).

---

## Where this fits in the full pipeline

| Step | What |
|------|------|
| **1 — Convert** | This page + `convert_to_markdown.py` |
| **2 — Assess** | Headings / structural scan / human skim |
| **3 — Fix loop** | Bespoke script or different built-in options; re-run until good |
| **3b — Semantic pass (optional)** | If still a mess: AI groups sentences by topic, names sub-topics, injects structure; **re-review** output before spec |
| **4 — Draft spec** | `draft_chunking_spec.py` → `markdown/structural_scan_report.*` + `memory/context_chunking_spec.yaml` |
| **5 — Chunk** | `chunk_markdown.py` |
| **6 — Embed** | `embed_and_index.py` |

Orchestrated one-shot: **`index_memory.py --path <source_folder>`** — see [process.md](../process.md).

CLI flags for convert only: [script-invocation.md](script-invocation.md).
