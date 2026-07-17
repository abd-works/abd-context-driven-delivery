---
name: abd-context-to-markdown
description: >-
  Convert office documents (PDF, PPTX, DOCX, XLSX, etc.) to navigable Markdown
  with real headings, sections, and tables. Use when the user wants to convert
  a document or folder of documents to markdown, mentions "convert to markdown",
  "extract text", or needs source files prepared for chunking or agent context.
context-fidelity:
  - level: context
license: MIT
metadata:
  author: agilebydesign
  version: "1.0.0"
---

# Convert to Markdown

Convert source documents to **navigable Markdown** — real headings, sections, and tables — so downstream tools (chunking, search) can follow structure instead of guessing it.

## Supported inputs

`.pdf`, `.pptx`, `.docx`, `.xlsx`, `.xls`, `.html`, `.htm`, `.txt`, `.csv`, `.json`, `.xml`

## How to convert

### Single file

```bash
python scripts/convert_to_markdown.py --file <file_path>
```

### Folder of documents

```bash
python scripts/convert_to_markdown.py --memory <source_folder>
```

Output goes to `<source_folder>/markdown/`, mirroring the original folder structure and filenames.

## After convert: assess structure

Chunking and RAG work best when markdown has real **sections** (headings), not a flat wall of text.

**Check:** Does the output have `#` / `##` / `###` where the source had chapters or sections? Run `draft_chunking_spec.py` (from the [abd-chunk-markdown](../abd-chunk-markdown/SKILL.md) skill) to get a structural scan report, or skim the markdown directly.

**If structure is bad** (few or no headings, wrong breaks):

1. Tell the user clearly what failed (e.g. "almost no `##`, chunking will be poor").
2. Suggest a fix:
   - Install **PyMuPDF** for PDF outline injection (`pip install pymupdf`)
   - Adjust env flags (`PDF_SKIP_*`) per [pdf-extraction-advanced.md](references/pdf-extraction-advanced.md)
   - Add a **bespoke post-processor** under `<topic_root>/scripts/` for this corpus
3. Implement, run, re-check. Repeat until structure is good enough to chunk.

**If it is still a wall of text** after fixes: run an **AI semantic pass** — group sentences by meaning, identify topics/sub-topics, add headings, complete one pass, then re-review before drafting a chunking spec.

## Built-in PDF post-processing

PDFs pass through `pdf_markdown_post` after extraction: banner collapse, conservative `CHAPTER` / `APPENDIX` / `PART` line promotion, optional outline alignment when PyMuPDF is installed. This is generic — corpus-specific fixes belong in `<topic_root>/scripts/`.

For deep PDF detail, see [references/pdf-extraction-advanced.md](references/pdf-extraction-advanced.md).

## Bespoke post-processors (corpus scripts)

When the default pipeline is not enough for a specific corpus, add scripts under **`<topic_root>/scripts/`** (the corpus folder, not this skill's `scripts/`). Name them clearly (`prepare_handbook_headings.py`, `dedupe_chapter_headers.py`). Document usage in the script docstring.

## Topic folder (where output goes)

**Workspace policy** (default corpus, config files): **[AGENTS.md](../../../AGENTS.md)** (*Workspace (topic root) — config first*).

**In practice:** set **`CONTENT_MEMORY_ROOT=`** in **`conf/.secrets`** (same agent root as `AGENTS.md`), or pass **`--path <folder>`** / **`--memory <folder>`**, or **`cd`** to the corpus before running. Markdown appears under `<source>/markdown/`. The code reads **`CONTENT_MEMORY_ROOT`** from the process environment after config files are loaded — keep the value in **`conf/.secrets`**, not only as a manual shell export.

## Dependencies

```bash
pip install "markitdown[all]"
# Optional: PDF bookmark outline → markdown headings
pip install pymupdf
```

## Gotchas

- For **PDFs**, the converter **tries `pdf_outline_extract` first** (PyMuPDF + non-empty `get_toc()`): section text is bounded by **bookmarks** (often much better for two-column books). If that is not used, it falls back to **MarkItDown** (linear stream). Install **PyMuPDF** and ensure `PDF_USE_MARKITDOWN_PDF` is not set. See [references/pdf-extraction-advanced.md](references/pdf-extraction-advanced.md) (*Two-column RPG*).
- Running headers in PDFs repeat on every page as text; `pdf_markdown_post` collapses them but may miss unusual patterns.
- PPTX charts are extracted as data tables, not images.
- The converter does not invent structure — if the source has no headings, neither will the markdown.
