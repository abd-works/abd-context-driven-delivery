# markdown

## Purpose

Extract co-located markdown — folder, file, or section — and convert that extract to HTML. Assembly of agent recipes is not this package.

## Seam (terms)

`@markdown`, `@markdownCollection`, `Markdown`, `MarkdownCollection`, `HTML`, `AssetLocator`, `AssetLocation`

## Dependencies (one-way)

none — location and extract live in this package

## Public API

- `Markdown.from_label(host, label).extract()` — `AssetLocator.locate` under the host class file directory and `host.name`.
- `Markdown.html()` — `HTML.from_markdown(extract())`.
- `Markdown.coerce(text, return_type)` — str, RulesCollection, templates path map, or HTML.
- `@markdown` — property name is the label; coerce to the annotated return type. File-kind marks (`@skill` / `@command` / `@rules` / `@mcp`) on the getter are copied through.
- `@markdownCollection` — same locate as `@markdown`; return type is a collection; `collection.markdown` is the original extract. List iterates bullets or folder files; map keys from bullet label or file stem.

Resolution order: `{label}/` folder, `{label}.md` file, then `## Label` in `{slug}.md`.
