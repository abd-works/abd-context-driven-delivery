# markdown

## Purpose

Extract co-located markdown — folder, file, or section — and convert that extract to HTML. Assembly of agent recipes is not this package.

## Seam (terms)

`@markdown`, `Markdown`, `HTML`, `AssetLocator`

## Dependencies (one-way)

`primitives/assets`

## Public API

- `Markdown.from_label(host, label).extract()` — `AssetLocator.locate` under the host class file directory and `host.name`.
- `Markdown.html()` — `HTML.from_markdown(extract())`.
- `Markdown.coerce(text, return_type)` — str, RulesCollection, templates path map, or HTML.
- `@markdown` — property name is the label; coerce to the annotated return type. File-kind marks (`@skill` / `@command` / `@rules` / `@mcp`) on the getter are copied through.

Resolution order: `{label}/` folder, `{label}.md` file, then `## Label` in `{slug}.md`.
