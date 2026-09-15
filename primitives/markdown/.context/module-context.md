# markdown

## Purpose

Extract co-located markdown for guidance hosts — single-label read seam wrapping `AssetLocator` / `markdown_extractor`. Assembly and deploy live elsewhere.

## Seam (terms)

`Markdown`, `@markdown`

## Dependencies (one-way)

`primitives/assets`

## Public API

- `Markdown.from_label(host, label).extract()` — resolve label under `host.context_guidance.module_dir` (or `host.module_dir`) and return extracted text.
- `@markdown` — property decorator; property name is the asset label.
