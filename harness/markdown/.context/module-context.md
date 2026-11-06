# markdown

## Purpose

Extract co-located markdown — folder, file, or section — and convert that extract to HTML. Assembly of agent recipes is not this package.

## Seam (terms)

`@markdown`, `@markdownCollection`, `Markdown`, `MarkdownCollection`, `HTML`, `AssetLocator`, `AssetLocation`, `Format`

## Dependencies (one-way)

none — location and extract live in this package

## Public API

- `Markdown.from_label(host, label).extract()` — `AssetLocator.locate` under the host class file directory and `host.name`.
- `Markdown.html()` — `HTML.from_markdown(extract())`.
- `Format(name)` / `Format.from_extension(extension)` — the one format vocabulary: `name` (`md` is `markdown`), `short`, `extension`, `is_code`, `is_known`, and where its templates are kept (`template_folder`, `template_extension`). Every reader of a format, an extension, or a template folder asks it.
- `Markdown.coerce(text, return_type)` — str, RulesCollection, templates path map, or HTML.
- `@markdown` — property name is the label; coerce to the annotated return type. File-kind marks (`@skill` / `@command` / `@rules` / `@mcp`) on the getter are copied through.
- `@markdownCollection` — same locate as `@markdown`; return type is a collection; `collection.markdown` is the original extract. List iterates bullets or folder files; map keys from bullet label or file stem.

Resolution order: `{label}/` folder, `{label}.md` file, then `## Label` in `{slug}.md`.
