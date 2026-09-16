# markdown

## Purpose

Extract co-located markdown — not assembly. Convert that extract to HTML.

## Seam (terms)

`@markdown`, `Markdown`, `HTML`, `AssetLocator`

## Dependencies (one-way)

`primitives/assets`

## Public API

- `Markdown.from_label(host, label).extract()` — `AssetLocator.locate` under the host class file directory and `host.name`. No `module_dir` on the host.
- `Markdown.html()` — `HTML.from_markdown(extract())`.
- `Markdown.coerce(text, return_type)` — str, RulesCollection, templates path map, or HTML.
- `@markdown` — property name is the label; coerce to the annotated return type. File-kind marks (`@skill` / `@command` / `@rules` / `@mcp`) on the getter are copied through.
