# cdd_guidance/actions

Each action is a *GuidanceAction*: *Generate*, *Validate*, *Document*, *Render*, *Satisfy*, *Sketch*, *Partition*, *Iterate*, *GrillContext*, *Improvement* (repair), and *Diagnose*. Importing the package registers every action folder's toolset with *ActionCatalogue*, and registers the practices first, since the actions work on them. The saved sketch is read by *SketchOutline* in cdd_guidance/practices/sketch_document, and each practice's section of it is a *SketchLens* in harness/guidance; neither lives here any more.

- **Purpose:** Give every practice the same generate, document, validate, satisfy, render, sketch, partition, grill, iterate, repair, and diagnose steps, so a practice owns only its words, rules, and formats.
- **Seam (terms):** Generate, Validate, Document, Render, Satisfy, Sketch, Partition, Iterate, GrillContext, Improvement, Diagnose
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/guidance, harness/guidance_actions, harness/installation, harness/mcp, harness/graph, cdd_guidance/practices (the package, which registers the practices)

## Generate : GuidanceAction

Write the artifacts each listed guidance asks for at its current fidelity.

------
----
+ generate(guidance: GuidanceArg): str
	-> GuidanceAction.run
+ generate_fixes_from_validate(): str
---<<creates>>--> Format
---<<reads fidelities of>>--> PracticeGuidance
---<<renders the earlier fidelity with>>--> Render
---<<lists as a tool>>--> Validate

## Validate : GuidanceAction

Check artifacts against each listed guidance's rules, add the graph rules' hits, and save the report.

+ Validate(session = None, call = None)
------
----
+ validate(guidance: GuidanceArg, rule: Rule | None = None, graph: bool | str | list[str] | None = None, paths: list[str] | None = None): str
+ create_rule(guidance: GuidanceArg, failed: str = '', wanted: str = ''): str
---<<validates with>>--> Rule
---<<reads the saved graph with>>--> SavedGraph
---<<annotated with>>--> NoDeploy
---<<annotated with>>--> Skill

## Document : GuidanceAction

Record what already exists for each listed guidance without correcting it.

------
----
+ document(guidance: GuidanceArg, paths: list[str]): str
---<<annotated with>>--> Skill

## Render : GuidanceAction

Convert already-generated content into another format.

------
----
+ render(guidance: GuidanceArg, format: str, paths: list[str] | str, content: str = '', source: str | None = None): list
	-> GuidanceAction.document_named
+ place_rendered(): str
+ answer_board_comment(board: str): str
	// the board's comment is answered in the file it was drawn from, never on the board alone

## Satisfy : GuidanceAction

Validate, fix from the report, and validate again.

------
----
+ satisfy(guidance: GuidanceArg): str
---<<lists as a tool>>--> Validate
---<<reads generate fixes from validate of>>--> Generate

## Sketch : GuidanceAction

Sketch a solution interactively before generating the formal artifact.

+ Sketch(agent_dir: str = '', session = None, call = None)
------
+ sketch_template: str
----
+ made_for(session, call = None): Sketch
+ find_template(agent_dir: str = ''): str
+ save_sketch(content: str = '', paths: list[str] | str | None = None, module: str = ''): str
+ list_sketches(module: str = ''): str
+ review_sketch(): str
+ sketch(guidance: GuidanceArg): str
---<<grills with>>--> GrillContext
---<<ends with the recipe of>>--> Generate

## Partition : GuidanceAction

Convert a corpus to markdown, split it into an index and verbatim segments, and embed the segments into a searchable index.

+ Partition(session: Any = None, call: ToolCall | None = None, context_setup: ContextSetup | None = None)
------
+ << composition >> context_setup: ContextSetup
+ context_index: ContextIndex
	// its context_setup's
----
+ made_for(session: Any, call: ToolCall | None = None): Partition
+ verify_segment_completeness(segment_path: str, expected_names: str = '', min_body_chars: int = MIN_ENTRY_BODY_CHARS, index_path: str = ''): str
+ partition_guidance(): str
+ index(context: str = '', out_root: str | None = None, paths: list[str] | str | None = None): str
+ segment(out_root: str | None = None): str
+ segment_files(out_root: str | None = None): list[str]
+ partition(guidance: GuidanceArg, context: str = '', mode: str = 'one_go', out_root: str | None = None, paths: list[str] | str | None = None): str

## Iterate : GuidanceAction

Grill, then generate and validate one small slice at a time.

------
----
+ mark_iterate_round(): str
+ iterate(guidance: GuidanceArg): str
---<<grills with>>--> GrillContext

## GrillContext : GuidanceAction

Interview a plan relentlessly against the codebase context until reaching shared understanding.

------
----
+ explore_context_files(folder: str = ''): str
+ read_context_file(path: str): str
+ write_grill_answer(heading: str, body: str): str
+ grill(guidance: GuidanceArg): str
+ grill_with_context(plan: str = '', paths: list[str] | str | None = None): str
---<<generates each answer with>>--> Generate

## Improvement : GuidanceAction

Repair a guidance's artifact for one violation, and re-check a repair theme.

------
----
+ repair_loop(): str
+ repair(guidance: GuidanceArg, asset: str = '', violation: str = ''): str
+ verify_fix(guidance: GuidanceArg, theme: str): str
---<<diagnoses with>>--> Diagnose
---<<annotated with>>--> Mcp

## Diagnose : GuidanceAction

Disciplined diagnosis loop for hard bugs and performance regressions.

------
----
+ diagnose(guidance: GuidanceArg | None = None): str
---<<annotated with>>--> SubAgentAnnotation
---<<annotated with>>--> NoCatalog
