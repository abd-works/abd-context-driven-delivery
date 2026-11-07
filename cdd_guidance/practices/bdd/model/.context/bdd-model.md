# BddModel

*BddModel* is one spec: descriptions, the contexts nested under them, and the observations (`it`) at every level. A sketch, a markdown tree, a Python (Mamba) spec, a TypeScript spec, and a saved knowledge graph all read into the same tree, and every format writes from it. `that` and `with` lines are contexts; the name carries the word.

Callers do not construct a format class directly. `Bdd.render` (through `PracticeGuidance.render`) picks the adapter `Bdd` lists under `formats` — `sketch`, `markdown`, `python`, `typescript`, `graph` — parses the source into a *BddModel*, and asks the target format's adapter to `render` it.

```
model = PythonBddModel().parse(text)
markdown = MarkdownBddModel().render(model)
```

# practices/bdd/model

- **Purpose:** Keep observable behaviour as one describe tree — descriptions, contexts, observations — so a sketch and a spec file stay the same hierarchy every later fidelity reads, and so the graph can check BDD rules against facts each node carries.
- **Seam (terms):** BddModel, MarkdownBddModel, SketchBddModel, CodeBddModel, PythonBddModel, TypeScriptBddModel, GraphBddModel, BehaviorNode, Description, Context, Observation, UnreadableSpec
- **Dependencies (one-way):** harness/graph (*ModelNode*, *ModelChildren*, *Graph*, *Node*, *Edge*), practices/clean_engineering/model (*CodeBody*, *CodeLanguage*, *WrittenBlock*, *CallGraphEntry*), actions/sketch (*SketchOutline*, *SketchLens*)

*ModelNode*, *ModelChildren*, *CodeBody*, *CodeLanguage*, *WrittenBlock*, and *CallGraphEntry* are owned by the modules above; this model only uses them.

## BehaviorNode : ModelNode

Every description, context, and observation. It knows its own source lines and the facts BDD graph rules read.

+ BehaviorNode(name: str, sequential_order: int = 1, graph: Graph | None = None)
------
+ name: str
+ sequential_order: int
+ line: int
+ end_line: int
+ written: WrittenBlock | None
	// how the block was written in the language it was read from; None when it came from a sketch or markdown
+ setup: CodeBody
	// the code above the first child: before blocks, shared fields, helpers. Empty outside code
+ expect_count: int
+ has_implementation: bool
+ private_probe: dict
	// the first line that asserts on, reads, or calls a private member; empty when there is none
----
+ take_code_from(source: BehaviorNode): None
	// keep written and setup, so a copy in another format can still write them back
+ load_span_facts(span: str): None
	// fills expect_count, has_implementation, private_probe from this node's own lines

## Description : BehaviorNode

+ Description(name: str, sequential_order: int = 1)
------
+ contexts: ModelChildren[Context]
+ observations: ModelChildren[Observation]
	// spec code often puts it straight under the outermost describe
----
+ clone(): Description
	// a copy with its contexts and observations

## Context : BehaviorNode

+ Context(name: str, sequential_order: int = 1)
	// a nested context is a context whose parent is a context
------
+ contexts: ModelChildren[Context]
+ observations: ModelChildren[Observation]
----
+ clone(): Context

## Observation : BehaviorNode

+ Observation(name: str, sequential_order: int = 1, graph: Graph | None = None)
------
+ body: CodeBody
	// the test body as read, in the language it was written in. Empty at behavior fidelity
+ call_graph: list[CallGraphEntry]
	// the realization: the calls this observation makes, written at realization fidelity
+ surface_lines: list[str]
	// the `->` lines that name what the observation calls first
----
+ take_code_from(source: Observation): None
	// also keeps body
+ clone(): Observation

## BddModel : ModelNode

The spec, and the sketch format: an indented describe tree, with an observation's realization in a fenced block above its `it` line.

+ BddModel(graph: Graph | None = None)
------
+ descriptions: ModelChildren[Description]
	// composition — a description has no spec outside this spec
+ preamble: CodeBody
	// the code above the first description as read: imports and helpers. Empty outside code
+ written: WrittenBlock | None
+ patches_infrastructure: bool
+ signature_marker: bool
+ top_level_describes: list[str]
+ code_like_describe_lines: list[int]
+ private_probe: dict
----
+ parse(text: str): BddModel
	// reads the indented sketch tree
+ parse_code(text: str): BddModel
	// each code format reads its own syntax
+ render(canonical: BddModel, previous: str | None = None): str
	// the indented sketch tree, with fenced realizations
+ load_source_facts(text: str): None
	// fills the facts the whole spec file owns
+ behavior_nodes(): list[BehaviorNode]
	// every description, context, and observation, parents first
+ setup_at(path: tuple): CodeBody
+ body_at(path: tuple): CodeBody
+ written_at(path: tuple): WrittenBlock | None
	// path is the names from the description down; empty or None when this spec has no such block

## MarkdownBddModel : BddModel

The `markdown` format. It reads and writes the same indented tree as *BddModel*.

## SketchBddModel : BddModel

The `sketch` format.

----
+ parse(text: str): BddModel
	// an integrated sketch: only its BDD section
	-> SketchOutline.body_for

## CodeBddModel : BddModel

A spec written as code. The walk and the rule for each body live here; a language only spells the lines.

------
+ language: CodeLanguage
----
+ parse(text: str): CodeBddModel
	-> check_readable(text)
	-> parse_code(text)
+ check_readable(text: str): None
	// raises UnreadableSpec when text is not valid code in this language
+ render(canonical: BddModel, previous: str | None = None): str
	Invariant: a block written in this language under the same name is written back exactly as read
	Invariant: a test body from another language is commented out above the signature marker, so development fidelity still counts every it that is not written in this language
	// previous set: each block keeps the previous file's setup or body when the canonical one is not in this language
	// an empty body: the realization call graph as comments, then marker_line
+ default_imports(): list[str]
+ top_level_gap(): list[str]
+ block_open(kind: str, name: str): str
	// kind is description, context, or it
+ block_close(): list[str]
+ empty_block(): list[str]
+ marker_line(): str
	// a line that holds the comment "BDD: SIGNATURE" and is valid as the whole body of an it

## PythonBddModel : CodeBddModel

The `python` format: Mamba `with description(...)`, `with context(...)`, `with it(...)`.

------
+ language: CodeLanguage
	// PYTHON (the code_body constant)
----
+ check_readable(text: str): None
+ parse_code(text: str): PythonBddModel
+ default_imports, top_level_gap, block_open, empty_block, marker_line
	// Python spelling only. The marker is `pass  # BDD: SIGNATURE`

## TypeScriptBddModel : CodeBddModel

The `typescript` format: `describe`, `context`, `it`, and Playwright's `test.describe` and `test`.

------
+ language: CodeLanguage
	// TYPESCRIPT (the code_body constant)
----
+ parse_code(text: str): TypeScriptBddModel
+ default_imports, block_open, block_close
	// TypeScript spelling only. The marker is `// BDD: SIGNATURE`

## GraphBddModel : BddModel

The `graph` format, read only: a saved knowledge graph read into descriptions whose observations carry their realization.

----
+ parse(text: str): GraphBddModel
	// the behaviour tree is the graph's bdd nodes in each spec file's order
	// each observation's call graph starts at what its invokes edges name and follows the Clean Engineering model's interactions (model_members), cut at a repeat or six calls deep
	-> Node.fact
	-> Edge.fact

## UnreadableSpec : ValueError

A spec file that is not valid code. Read as an empty spec, a render over it would replace every test body.

+ UnreadableSpec(language: str, error: SyntaxError)
------
+ line: int
----
