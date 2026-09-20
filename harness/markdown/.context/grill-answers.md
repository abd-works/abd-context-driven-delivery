# Grill Answers

### Markdown collection replaces twin *_markdown properties

Forget nested toolsets for now. `@markdown` already locates folder / file / section and, when the return type is RulesCollection, already builds a collection from bullets (`harness/markdown/markdown.py`, `RulesCollection.from_markdown`). The pain is the twin `rules` + `rules_markdown` pair on Guidance. An annotated collection (`@markdownCollection("shared rules")`) is the same locate; list vs map comes from the return type (bullets or folder files; map keys from bullet label or file stem). The collection keeps `.markdown` as the original extract — one file stays that file — so inject, install, and instructions read `rules.markdown` and `rules_markdown` goes away.

### Markdown-collection sketch agreed

Sketch at harness/markdown/.context/markdown-collection-sketch.md is agreed: @markdownCollection reuses @markdown locate; collection.markdown is the original extract; rules_markdown is dropped; @rules lives on rules.

