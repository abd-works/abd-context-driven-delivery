# harness/markdown

*Markdown* is the prose a property loads from a folder, file, or section beside its class, located once from the *MarkdownScope* its owner hands over; *MarkdownText* reads a document's headings and sections; *Format* names the channel an artifact is written in. The whole model of this module, internals included, is `harness/markdown/.context/markdown-collection-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let a class keep its words in markdown beside it, read them back typed, and convert them to HTML.
- **Seam (terms):** Markdown, MarkdownScope, MarkdownCollection, MarkdownText, FrontMatter, Format, `operation_property`; the annotations `@markdown` and `@markdown_collection`
- **Dependencies (one-way):** harness/annotations

## Markdown

The prose one property loads: the folder or file named after the property, or the section titled after it, located once and read once.

+ Markdown(instance: Any, label: str, fidelity: str | None = None, format: str | None = None)
------
+ location: AssetLocation
+ document: MarkdownText
----
+ from_label(instance: Any, label: str, fidelity: str | None = None, format: str | None = None): Markdown
+ held_by(owner: Any, label: str): Markdown
	// one Markdown per label and scope, kept on the owner, so a second read answers from the text the first found
+ extract(): str
+ expand_docstring(docstring: str | None): str
+ html(): HTML
+ coerce(text: str, return_type: Any): Any
+ built_by(from_markdown: Callable[..., Any], text: str, parent: Any): Any
+ read_into(return_type: Any, build: Callable[..., Any] | None = None): Any
+ return_type_of(fn: Callable[..., Any], default: Any): Any
---<<locates its section from>>--> MarkdownScope
---<<reads sections with>>--> MarkdownText
---<<reads template folders of>>--> Format
---<<creates>>--> Name

## MarkdownScope

Where an owner keeps its markdown and which part of it the owner reads: the folder beside its class, the slug its `{slug}.md` is named by, and the fidelity and format whose templates and examples it reads. An owner that knows these hands them over as its `markdown_scope` property.

+ MarkdownScope(folder: Path, slug: str, fidelity: str | None = None, format: str | None = None, in_fidelity_block: bool = False)
------
+ folder: Path
+ slug: str
+ fidelity: str | None
+ format: str | None
+ in_fidelity_block: bool
----
+ beside(owner_class: type): MarkdownScope
+ of(owner: Any): MarkdownScope
+ at(fidelity: str | None = None, format: str | None = None): MarkdownScope

## MarkdownCollection

Listed or keyed extracts that keep the original markdown. `@markdown_collection` annotates the property that holds one.

+ MarkdownCollection(entries: dict[str, Any] | list[Any] | None = None, parent: Any = None)
------
+ entries: dict[str, Any] | list[Any]
+ parent: Any
+ markdown: str
----
+ child(name: str, body: str = ''): Any
+ from_markdown(text: str, parent: Any = None): MarkdownCollection
+ from_section(markdown: Markdown, return_type: Any, parent: Any = None): Any
+ attach(instance: Any, name: str | None = None): None
---<<calls built_by on>>--> Markdown
---<<creates>>--> MarkdownText
---<<annotated with>>--> HostedOnly

## MarkdownText

A markdown document: headings, slices, and child sections.

+ MarkdownText(text: str)
------
+ text: str
+ yaml_fields: dict[str, Any]
+ without_yaml: str
----
+ headings(): list[tuple[int, int, int, str]]
+ slice_heading(heading: str): str
+ child_blocks(parent_heading: str): list[tuple[str, str]]
+ section_child_blocks(): list[tuple[str, str]]
+ fidelity_blocks(): list[tuple[str, str]]
+ fidelity_block(fidelity_name: str): str
+ named_subsection(heading: str): str

## FrontMatter

The settings at the top of a file: a YAML block between `---` lines, or, in a code template, the same block written as `# ---` comment lines.

+ FrontMatter(text: str)
------
+ text: str
+ settings: str
+ fields: dict[str, str]
+ content: str
----
+ of_file(path: Path): FrontMatter

## Format

*Format* is a channel an artifact is written in, such as `markdown`, `python`, or `drawio`.

+ Format(name: str | None)
------
+ name: str
+ short: str
+ extension: str
+ is_code: bool
+ group: str
+ group_order: int
+ file_order: int
+ is_templated: bool
+ template_folder: str
+ template_extension: str
----
+ from_extension(extension: str): Format
