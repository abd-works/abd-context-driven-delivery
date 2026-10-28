# Spec

*Spec* reads a path into descriptions, contexts, and observations. A nested description is a description whose parent is a description. A nested context is a context whose parent is a context. `that` and `with` are contexts; the name carries the word. Markdown, Python, TypeScript, and Java continue through observations. Every channel uses the same walk. A channel only differs in how the next node is taken out of the path: the next block in a file, or the next spec file in a folder.

Callers use the base nodes. `BddModelFactory.load` takes a file or a folder, chooses the channel spec, and returns a `Spec`.

```
spec = BddModelFactory.load(path)
```

# practices/bdd/model

- **Purpose:** Keep observable behaviour as one spec — descriptions and contexts, then observations — so a sketch and a test file stay the same hierarchy every later fidelity reads.
- **Seam (terms):** BddNode, BddModelFactory, Spec, Description, Context, Observation
- **Dependencies (one-way):** *(none)*

## BddNode

Every spec, description, context, and observation is a BddNode. A channel node extends the same base, so a MarkdownDescription and a PythonDescription share name, order, and parent.

+ BddNode(source: BddNode)
	// copies name, sequential order, and written
------
+ name: str
+ sequential_order: int
+ parent: BddNode
+ written: WrittenBlock | None
	// how this block was written in code. None when it came from a sketch or markdown
----
+ semantic_type(): str
	// Spec, Description, Context, or Observation
+ clone(): BddNode
	// a copy of this node, including its children

## WrittenBlock

The source text around one describe, context, or it that the model has no node for, kept exactly as read so the same language writes it back unchanged.

+ WrittenBlock(language: CodeLanguage, name: str)
------
+ language: CodeLanguage
+ name: str
	// the block's name when read. A renamed block is written with the generic opening
+ lead: str
	// the text between the previous sibling and this block: blank lines, comments, and code such as helpers
+ heading: str
	// the opening as written, every line of it, for example with description("x") as self:
+ closing: str
	// the text after the last child, inside the block
+ close: str
	// the closing line as written, for example }); in TypeScript. Empty in Python
----
+ is_in(language: CodeLanguage, name: str): bool
	// written in this language under this name, so the raw text still holds
+ lead_body(): CodeBody
	// the lead as a CodeBody, for writing it commented out in another language

## BddModelFactory

+ load(path: str): Spec
	// path is a file, or a folder of spec files
	// the file type, or the files in the folder, selects the channel spec
	// that spec loads itself
	// the return is a Spec

## Spec : BddNode

+ Spec(source: Spec)
	// source empty: the spec is empty until load
	// source set: descriptions are this channel's types, built from source. A nested description uses description_type
	// the new spec does not keep the source's channel types
------
+ file: str
+ preamble: CodeBody
	// the code above the first description as read: imports and helpers. Empty outside code
+ closing: str
	// the code after the last description, as read. Empty outside code
+ descriptions: list[Description]
	// composition — a description has no spec outside this spec
	// a nested description is a description whose parent is a description
+ description_type: type
----
+ load(file: str): Spec
	// stores file, then runs the same walk for every channel
	self.file = file
	self.load_spec_content()
	self.load_descriptions()
+ save(): str
	// every channel writes its file with this operation
- load_spec_content(): None
	// channel prepares its cursor over file
	// a single file stores that file
	// a folder stores the path-to-content map: one spec file per top-level description
- load_descriptions(): None
	// while has_more_description: append load_next_description()
- has_more_description(): bool
	// channel: another top-level description remains in the path
- load_next_description(): Description
	// description = get_next_description_from_file()
	// -> description.load_children()
- get_next_description_from_file(): Description
	// channel: the next description shell from the path, in description_type

## Description : BddNode

+ Description(source: Description)
	// copies name and order
	// a nested description is a description whose parent is a description
	// each source child description becomes this channel's description
	// each source context becomes this channel's context
------
+ setup: CodeBody
	// everything in the block that is not a child: before blocks, shared fields, helpers. Empty outside code
+ descriptions: list[Description]
+ contexts: list[Context]
+ observations: list[Observation]
	// spec code often puts it straight under the outermost describe
+ description_type: type
+ context_type: type
----
+ append_description(description: Description): None
+ append_context(context: Context): None
- load_children(): None
	// while a child remains, in file order
	// the next child is a description: load_next_description()
	// the next child is a context: load_next_context()
- has_more_description(): bool
	// channel: the next child is a description
- load_next_description(): Description
	// child = get_next_description_from_file()
	// -> child.load_children()
- get_next_description_from_file(): Description
	// channel: the next child description, in description_type
- has_more_context(): bool
	// channel: the next child is a context
- load_next_context(): Context
	// context = get_next_context_from_file()
	// -> context.load_children()
- get_next_context_from_file(): Context
	// channel: the next context shell, in context_type

## Context : BddNode

+ Context(source: Context)
	// copies name, order, and setup
	// a nested context is a context whose parent is a context
	// that and with stay contexts; the name carries the word
	// each source child context becomes this channel's context
	// each source observation becomes this channel's observation
------
+ setup: CodeBody
	// everything in the block that is not a child, as read: the before block that establishes the state named in this context, shared fields, helpers. Empty when the file has none
+ contexts: list[Context]
+ observations: list[Observation]
+ context_type: type
+ observation_type: type
----
+ append_context(context: Context): None
+ append_observation(observation: Observation): None
- load_children(): None
	// while a child remains, in file order
	// the next child is a context: load_next_context()
	// the next child is an observation: load_next_observation()
	// a before block fills setup and is not a child
- has_more_context(): bool
	// channel: the next child is a context
- load_next_context(): Context
	// child = get_next_context_from_file()
	// -> child.load_children()
- get_next_context_from_file(): Context
	// channel: the next child context, in context_type
- has_more_observation(): bool
	// channel: the next child is an observation
- load_next_observation(): Observation
	// observation = get_next_observation_from_file()
- get_next_observation_from_file(): Observation
	// channel: the next observation shell, in observation_type

## Observation : BddNode

+ Observation(source: Observation)
	// copies name, order, and body
------
+ body: CodeBody
	// the test body as read, in the language it was written in. Empty at behavior fidelity
	// a code spec writes it with CodeBody.lines_in: the body in the same language, otherwise the signature marker

## MarkdownBddNode

+ strip_markup(text: str): str
	// the hierarchy line without a leading it. Description, context, and observation names are read through this

## MarkdownSpec : Spec

+ MarkdownSpec(source: Spec)
------
+ description_type: MarkdownDescription
----
- load_spec_content(): None
	// cursor is the indented hierarchy lines in file
- has_more_description(): bool
- get_next_description_from_file(): MarkdownDescription
+ save(): str

## MarkdownDescription : Description, MarkdownBddNode

+ description_type: MarkdownDescription
+ context_type: MarkdownContext
----
- has_more_description(): bool
	// the next line is a subject. A line that starts with that or with is a context
- get_next_description_from_file(): MarkdownDescription
- has_more_context(): bool
- get_next_context_from_file(): MarkdownContext

## MarkdownContext : Context, MarkdownBddNode

+ context_type: MarkdownContext
+ observation_type: MarkdownObservation
----
- has_more_context(): bool
	// the next line starts with that or with
- get_next_context_from_file(): MarkdownContext
- has_more_observation(): bool
	// the next line starts with it or should
- get_next_observation_from_file(): MarkdownObservation

## MarkdownObservation : Observation, MarkdownBddNode

## CodeBddNode

+ slug(): str
+ snake(): str
	// the spec file name for a top-level description
+ name_from_slug(slug: str): str
	// the name read back from a spec file

## CodeSpec : Spec

+ CodeSpec(source: Spec)
	// file for load is the path-to-content map when the path is a folder
------
+ description_type: CodeDescription
----
- load_spec_content(): None
	// cursor is one spec file, or one spec file per top-level description
- has_more_description(): bool
- get_next_description_from_file(): CodeDescription
+ save(): str
	// one spec file per top-level description. A nested description stays in that file
+ language: CodeLanguage
	// each language spec sets its instance, shared with the clean engineering code channels
+ render(canonical: Spec, previous: str | None): str
	// the one spec render. Every language writes through this walk and changes only how a line is spelled
	// previous set: each block keeps the previous file's setup or body when the canonical one is not in this language
	// preamble, else default_imports, then each description
- render_block(node: BddNode, parents: tuple, first: bool): list[str]
	// parents is the path of names above this block; its length is the depth
	// written in this language under the same name: lead, heading, setup, children, closing, close exactly as read
	// otherwise: one blank line, the lead commented out, block_open, setup, children in file order (sequential_order), block_close
- render_body(observation: Observation, path: tuple, written: WrittenBlock | None): list[str]
	// a body in this language: body.lines_in
	// an empty body: the realization call graph as comments, then marker_line
	// a body from another language: its text commented out, then marker_line
	// so the development fidelity still counts every it that is not written in this language
- default_imports(): list[str]
- block_open(kind: str, name: str): str
	// kind is description, context, or it
- block_close(): list[str]
- empty_block(): list[str]
	// what an empty description or context needs to stay valid code
- marker_line(): str
	// a line that holds language.comment("BDD: SIGNATURE") and is valid as the whole body of an it
	// each language overrides the spelling operations above. None of them decides what a body holds

## CodeDescription : Description, CodeBddNode

+ description_type: CodeDescription
+ context_type: CodeContext
----
- has_more_description(): bool
- get_next_description_from_file(): CodeDescription
- has_more_context(): bool
- get_next_context_from_file(): CodeContext

## CodeContext : Context, CodeBddNode

+ context_type: CodeContext
+ observation_type: CodeObservation
----
- has_more_context(): bool
- get_next_context_from_file(): CodeContext
- has_more_observation(): bool
- get_next_observation_from_file(): CodeObservation

## CodeObservation : Observation, CodeBddNode

## PythonBddNode : CodeBddNode

+ is_description(block: str): bool
	// the block is with description
+ is_context(block: str): bool
	// the block is with context
+ is_observation(block: str): bool
	// the block is with it
+ before_setup(block: str): str
	// the body of with before. Empty when the block is not a before

## PythonSpec : CodeSpec

+ PythonSpec(source: Spec)
------
+ description_type: PythonDescription
+ language: CodeLanguage
	// CodeLanguage.named("python")
----
+ save(): str
- default_imports, top_level_gap, block_open, block_close, empty_block, marker_line
	// Python spelling only. The marker is `pass  # BDD: SIGNATURE`

## PythonDescription : CodeDescription, PythonBddNode

+ description_type: PythonDescription
+ context_type: PythonContext
----
- has_more_description(): bool
	// -> is_description
- get_next_description_from_file(): PythonDescription
- has_more_context(): bool
	// -> is_context
- get_next_context_from_file(): PythonContext

## PythonContext : CodeContext, PythonBddNode

+ context_type: PythonContext
+ observation_type: PythonObservation
----
- has_more_context(): bool
- get_next_context_from_file(): PythonContext
	// -> before_setup fills setup
- has_more_observation(): bool
	// -> is_observation
- get_next_observation_from_file(): PythonObservation

## PythonObservation : CodeObservation, PythonBddNode

## TypeScriptBddNode : CodeBddNode

+ is_description(block: str): bool
	// the next describe names a subject
+ is_context(block: str): bool
	// the next describe starts with that or with
+ is_observation(block: str): bool
	// the block is it
+ before_setup(block: str): str
	// the body of beforeEach. Empty when the block is not a beforeEach

## TypeScriptSpec : CodeSpec

+ TypeScriptSpec(source: Spec)
------
+ description_type: TypeScriptDescription
+ language: CodeLanguage
	// CodeLanguage.named("typescript")
----
+ save(): str
- default_imports, top_level_gap, block_open, block_close, empty_block, marker_line
	// TypeScript spelling only. The marker is `// BDD: SIGNATURE`

## TypeScriptDescription : CodeDescription, TypeScriptBddNode

+ description_type: TypeScriptDescription
+ context_type: TypeScriptContext
----
- has_more_description(): bool
	// -> is_description
- get_next_description_from_file(): TypeScriptDescription
- has_more_context(): bool
	// -> is_context
- get_next_context_from_file(): TypeScriptContext

## TypeScriptContext : CodeContext, TypeScriptBddNode

+ context_type: TypeScriptContext
+ observation_type: TypeScriptObservation
----
- has_more_context(): bool
- get_next_context_from_file(): TypeScriptContext
	// -> before_setup fills setup
- has_more_observation(): bool
	// -> is_observation
- get_next_observation_from_file(): TypeScriptObservation

## TypeScriptObservation : CodeObservation, TypeScriptBddNode

## JavaBddNode : CodeBddNode

+ is_description(block: str): bool
	// the next @Nested class names a subject
+ is_context(block: str): bool
	// the next @Nested class starts with that or with
+ is_observation(block: str): bool
	// the member is an @Test method
+ before_setup(block: str): str
	// the body of @BeforeEach. Empty when the member is not a before

## JavaSpec : CodeSpec

+ JavaSpec(source: Spec)
------
+ description_type: JavaDescription
----
+ save(): str

## JavaDescription : CodeDescription, JavaBddNode

+ description_type: JavaDescription
+ context_type: JavaContext
----
- has_more_description(): bool
	// -> is_description
- get_next_description_from_file(): JavaDescription
- has_more_context(): bool
	// -> is_context
- get_next_context_from_file(): JavaContext

## JavaContext : CodeContext, JavaBddNode

+ context_type: JavaContext
+ observation_type: JavaObservation
----
- has_more_context(): bool
- get_next_context_from_file(): JavaContext
	// -> before_setup fills setup
- has_more_observation(): bool
	// -> is_observation
- get_next_observation_from_file(): JavaObservation

## JavaObservation : CodeObservation, JavaBddNode

`Spec`, `Description`, `Context`, and `Observation` are `BddNode`s. A nested description is a description whose parent is a description. A nested context is a context whose parent is a context. `Spec` loads the top-level descriptions. `Description.load_children` loads the next description or context in file order. `Context.load_children` loads the next context or observation in file order, and a before block fills `setup`. Every spec implements `save(): str`. A markdown node is a `MarkdownBddNode`: `strip_markup`. Markdown is one sketch file: a subject line is a description, a `that` or `with` line is a context, and an `it` or `should` line is an observation. A code node is a `CodeBddNode`: `slug`, `snake`, and `name_from_slug`. A code folder is one spec file per top-level description; a nested description stays in that file. Python, TypeScript, and Java extend the code types and their own channel node. A Python node is a `PythonBddNode`. A TypeScript node is a `TypeScriptBddNode`. A Java node is a `JavaBddNode`. Each of those reads `is_description`, `is_context`, `is_observation`, and `before_setup` for the spelling that language uses. A channel overrides only `has_more_*` and `get_next_*_from_file` for the nodes its path contains. `load_next` stays on the base node. No channel stops before observations.
