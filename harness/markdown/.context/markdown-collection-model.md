# markdown collection — class model on `markdown.py`

Not a second Markdown. Collection shape lives on *MarkdownCollection*. *Markdown.coerce* stays HTML / str / dict / `from_markdown` — it does not test list. *YamlFields* and *MarkdownText* are in the same file; *RulesCollection* and *Guidance* belong to `harness/guidance` and appear here only as callers.

**Out of scope:** nested toolsets, *GuidanceCollection* (a *MarkdownCollection* subclass in `harness/guidance`), fidelities, *ToolSetCollection*.

---

## Language companion

*`@markdownCollection`* locates through *Markdown.from_label*, then *MarkdownCollection.from_section*. The collection keeps **markdown** as the original extract. One file is that file. Never rebuild from `formatted()`.

*MarkdownCollection* owns list vs map. A **list** return type iterates section bullets or files in the folder. A **map** return type keys each entry by the bullet label or the file stem. A return type with *from_markdown* (including *RulesCollection*) is that builder, then **markdown** is stamped.

*Guidance.rules* is that collection. *RulesCollection.inject_rules* and *Guidance.instructions* read **rules.markdown**. There is no *rules_markdown*.

---

## MarkdownCollection

MarkdownCollection(entries: dict | list | None = None, parent: Any = None)
------
entries: dict[str, Any] | list[Any]
	# each entry's parent is set to this collection
parent: Any
markdown: str
	# must be the original extract; never a formatted() rebuild
	# one file → that file
yaml: dict[str, str]
	# leftover yaml keys as string values
----
child(name: str, body: str) -> Any
	# none here; a subclass such as GuidanceCollection makes one entry per section block
from_markdown(text: str, parent: Any = None) -> MarkdownCollection
	# one entry per section child block, keyed by its name
	-> MarkdownText.section_child_blocks
	-> child
	-> YamlFields.assign_yaml
from_section(markdown: Markdown, return_type, parent: Any = None) -> Any
	# list → from_markdown of the extracted section
	# return_type.from_markdown → that builder (Markdown.built_by), keeping the section's text on the result
	# else from_markdown
attach(instance: Any, name: str | None = None) -> None
	# the owner keeps this same collection, so later reads return it
markdown_collection(fn | label: str | None) -> property
	# exported as markdownCollection
	# getter -> Markdown.from_label
	# getter -> Markdown.read_into(return_type, MarkdownCollection.from_section)
	# getter -> result.attach(owner, name)
	# never Markdown.coerce

## Guidance (caller)

rules: RulesCollection
	# @markdownCollection("shared rules")
	# @rules lives on this member
	# glob and matches live on RulesCollection — not MarkdownCollection
instructions
	# -> rules.markdown
	# never rules_markdown

## RulesCollection (caller)

inject_rules(payload: HookPayload)
	# -> matches
	# -> markdown
