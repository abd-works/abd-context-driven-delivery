# markdown collection — delta on live `markdown.py`

Not a second Markdown. Collection shape lives on *MarkdownCollection*. *Markdown.coerce* stays HTML / str / dict / `from_markdown` — it does not test list.

**Out of scope:** nested toolsets, *GuidanceCollection*, fidelities, *ToolSetCollection*.

---

## Language companion

*`@markdownCollection`* locates through *Markdown.from_label*, then *MarkdownCollection.coerce*. The collection keeps **markdown** as the original extract. One file is that file. Never rebuild from `formatted()`.

*MarkdownCollection* owns list vs map. A **list** return type iterates section bullets or files in the folder. A **map** return type keys each entry by the bullet label or the file stem. A return type with *from_markdown* (including *RulesCollection*) is that builder, then **markdown** is stamped.

*Guidance.rules* is that collection. *inject_rules* and *instructions* read **rules.markdown**. There is no *rules_markdown*.

---

## New

MarkdownCollection()
------
markdown: str
	# must be the original extract; never a formatted() rebuild
	# one file → that file
yaml: dict
	# leftover yaml keys as string values
----
coerce(markdown: Markdown, return_type) -> Any
	# list → from_list
	# return_type.from_markdown → keep_extract
	# else from_markdown
from_list(markdown: Markdown) -> MarkdownCollection
	# EXTEND: one entry per section bullet or folder file
from_markdown(text: str) -> MarkdownCollection
	# EXTEND: map → key = bullet label or file stem
keep_extract(result, text)

markdown_collection(label: str | None)
	# -> Markdown.from_label
	# -> MarkdownCollection.coerce
	# never Markdown.coerce

## Guidance (caller delta)

rules: RulesCollection
	# @markdownCollection("shared rules")
	# @rules lives on this member
	# glob and matches live on RulesCollection — not MarkdownCollection
inject_rules
	# -> rules.matches
	# -> rules.markdown
instructions
	# -> rules.markdown
	# never rules_markdown
