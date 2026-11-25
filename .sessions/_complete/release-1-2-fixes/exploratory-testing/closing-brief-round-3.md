# Closing round 3's gaps — what differs from `closing-brief.md`

Read `closing-brief.md` in this folder first: what you produce per defect (scenario, test written first at the tier that owns it, smallest fix), the guardrails and their four questions, how to run specs, and the report all hold. This file adds what is particular to round 3.

## Which defects

Every `defects/r3-*.md` file your card names counts as confirmed; round 3 had no confirmation pass, so reproduce each one from its Steps before you write its test, and report "does not reproduce" with what you ran when it does not. The round's summary is `round-3-report.md`. The testers' sandboxes hold the files each report used: `C:\dev\_et\round3\<robot>\work` and the five practices combined in `C:\dev\_et\round3\combined\work`; copy what you need into your spec's own fixtures, and never write in a sandbox.

## The person's answers (2026-11-20), which are now the promised behaviour

1. **Links and callouts in the Files app.** The Rendered view and the Source view both show callouts and both follow links. Which callouts show follows the file view's filters: the practices chosen and the graph's connectors. A callout is traversable as the graph tree is: from the story map a person opens a scenario in place, then what it observes, then an operation of the class.
2. **A step's linked domain term is an edge** from the step to the DDD class it links to. **UX joins the graph**: its screens, regions, controls, interactions and transitions are nodes, with edges to the stories a screen shows and the domain terms it names.
3. **One class in several practices is several nodes joined by edges.** A DDD entity is a kind of class: the DDD node has an "is a" edge to the Clean Engineering class node read from the same file, and following it reveals the Clean Engineering details. A module relates to an aggregate or a bounded context the same way, by an ordinary edge, though both are read from one folder. A class in a model document and the class in code that implements it are two nodes with an edge; neither replaces the other when both are loaded. Nothing is joined on a name alone: a call or a link goes to the node the file's own imports, path or link target name.
4. **Selecting in the graph tree.** Selecting a parent shows the parent in its file, where its children can be opened in place. Selecting a child, including a member under a relationship group such as invokes, shows only the child, in the child's own file.

Questions the person has not answered stay closed to you: `r3-gizmo-03`, `r3-rivet-11`, `r3-pixel-08`. Report them as "needs the person's decision".

## Who owns which files

Eight robots write in this checkout at once. Change only your own files; when a fix needs a change in another robot's files, write exactly what you need in your report under "needed from <robot>" and leave it.

| Robot | Owns | Defects |
|---|---|---|
| Sparky | `cdd_guidance/practices/stories/` except its graph reading and links: the format adapters under `model/` (markdown, drawio, whiteboard, python, typescript), templates, rules, the thin slice | r3-sparky-01, 02, 04, 06, 07, 10, 11; widget-06, widget-19 |
| Bolt | `cdd_guidance/practices/ddd/`, its graph reading included | r3-bolt-01 to 07; widget-20; the DDD side of answer 3 (the "is a" edge to the Clean Engineering class, aggregate and bounded context to module) |
| Gizmo | `cdd_guidance/practices/ux/`, and a new UX graph reading | r3-gizmo-01, 02, 04, 05, 06 (answer 2) |
| Widget | `cdd_guidance/practices/clean_engineering/`, its graph reading included | r3-widget-01 to 10; widget-08, widget-15 is a question, leave it |
| Rivet | `cdd_guidance/practices/bdd/`, its graph reading included | r3-rivet-01 to 10; r3-cog-01 (an observation is linked by what its spec imports) |
| Cog | `harness/graph/`, and the Stories graph reading and links (`cdd_guidance/practices/stories/model/graph_reading.py`, `StoryLinks` and what they import only for the graph) | r3-cog-02, 03, 04, 05; r3-sparky-03, 05 (answer 2), 08, 09 |
| Pixel | The Files app's file view: `harness/files_app/app/files/file-rendering.ts`, `file-view.tsx`, `file-source-view.tsx`, their specs and styles, and the callout code they use | r3-pixel-01, 02, 03, 04, 05, 07, 09 (answer 1) |
| Lens | The Files app's graph view and file lists: the graph tree and node selection in `harness/files_app/app`, and the Python they call in `space/session` (file manager, `session.graph_*`, which files a fidelity lists) | r3-lens-01 to 09; r3-pixel-06 (answer 4) |

A graph reading that needs a new node or edge kind in `harness/graph` asks Cog for it in its report and, until the lead passes that on, uses what `harness/graph` already offers.

**Another chat also works in this checkout**, lately in `harness/files_app/app` and `cdd_guidance/practices/stories`. Before you edit a file, look at `git status` and `git log -3 -- <file>`: when someone else has uncommitted edits in it, or it changed since you read it, read it again and make your change beside theirs. Never revert or overwrite a change you did not make.

## Order

Work the defects that lose or overwrite a person's content first, then wrong results in the graph, then misleading messages, then cosmetic ones. Stop and report when your defects are done or when you have worked about three hours; say what is not reached.

## Second answers from the person (2026-11-20), and the third wave

These are promised behaviour too. Five robots write in this checkout at once; the ownership rule above holds, with these owners.

| Robot | Work | Owns |
|---|---|---|
| Pixel | **Callout filtering moves to Python.** Which callouts a file shows is decided in Python by the same filter code that narrows the knowledge graph (`harness/graph` Filter, as `session.graph_trees` applies it with the node filter and the file list). The page sends its filter (practices, stages, formats, node types, connectors) with the read of the file and draws what comes back; `file-callouts.ts` keeps no rule of its own. Every application gets all business logic from Python: TypeScript, the cdd server, the Python adapter, no exception. Look for any other rule the Files app's file view decides on the page and move it the same way; report what you find and did not move. | `harness/files_app/app/files/file-callouts.ts`, `rendered-callouts.ts`, `file-view.tsx`, `file-source-view.tsx`, their specs; `space/session/session_file.py` and what `session.file` calls |
| Lens | **Fix button on failures.** A failure in display (a file that cannot be shown, a link to a file or heading that is not there, a graph view that fails), in a render or generate action, or in the session's roots shows a Fix button. Pressing it lists the most common causes of that failure and sends them, with the failure, to the AI to fix. The causes come from Python (see `failure.describe` and the chat bar's Fix buttons, which start `debug_session` with choice fix); the page only shows them and sends. Start with the Files app, then the board's fidelity outputs. | New files for the failure's band and button in `harness/files_app/app`, the Python that describes a failure and its causes; in files Pixel owns, add only the one line that mounts your component, last, after reading the file again |
| Anvil | **Diagnose and align.** A button on the context viewer (the Files app) that goes through the session's graph and its selected stages, fidelities and formats and reports the gaps: a chosen format with no file, formats of one fidelity whose graphs differ (nodes or edges in one and not the other), callouts that do not match the graph's edges. Align then renders to bring the formats in step, and each failure it meets can be sent to be fixed (Lens's Fix button; until it is there, answer the failure as data). Python first: the diagnosis and the alignment are domain objects in `space/session` with cdd server tools, proven by a heavy spec on a real project with a gap in it; the button comes last, in its own component. | New Python in `space/session`, a new component in `harness/files_app/app`; one mounting line in the page view, last |
| Gizmo | **Mockup associations, and TypeScript to JavaScript.** A mockup's whiteboard and drawing associate each screen and each control with the stories, scenarios and steps it serves, read back without loss and joined in the graph by edges. Nothing more is asked of those drawings (no states, interactions, descriptions). Front-end views render between TypeScript and JavaScript both ways. | `cdd_guidance/practices/ux/` |
| Cog | **A Then observes an Example only where a model is written.** The rule that every Then observes an Example, and the step-to-class edge for a linked domain term, apply to a story only when a domain model or a class model has been written for that area of the story graph. Where none is written, a scenario may link terms it comes up with and the graph raises nothing. Say in the rule's own words how "that area" is decided, from what the graph already holds. **Java stays removed**: check nothing in BDD, Stories or Clean Engineering still offers, names or documents Java for specs; specs are Python, TypeScript or JavaScript, and JavaScript is offered wherever TypeScript is. | `cdd_guidance/practices/stories/` rules and graph reading, `cdd_guidance/practices/bdd/`, `harness/graph/` |

New behaviour (Lens's button, Anvil's button, Pixel's moved filter) is Flow A: run it for real, capture it in a heavy or e2e test, then the unit tests. For a screen, save a screenshot of each step under `round-3-fix-shots/<robot>-wave3/`. Each new behaviour gets its story on `.context/story-map.md` and its scenarios under `story_tests/`, written with the Stories rules.

## Third answers from the person (2026-11-20), and the fourth wave

Promised behaviour. Four robots write here at once; the ownership rule above holds.

| Robot | Work | Owns |
|---|---|---|
| Anvil | **Every render ends in a saved file.** A render to Python, TypeScript or JavaScript saves its output at the paths the fidelity declares (one file per story, per aggregate, per class, per spec, as the fidelity writes them), as a render to drawio, whiteboard or markdown is saved today, and its result names the saved files. No render answers content for the agent to save. A file a person changed is kept by the same rules a saved drawing uses; say what those are for code. A whiteboard file still goes on to its board with publish_board. Closes r3-bolt-06 and r3-sparky-07. `session.align_formats` then aligns code formats too. | `cdd_guidance/actions/render/`, where a render is saved (`RenderedFile` and what it calls), `space/session/format_alignment.py` |
| Gizmo | **Diagram means drawio and whiteboard.** At UX mockup the drawing and the whiteboard are formats a person picks on the board, under the diagram chip that chooses both, saved under the epic's `.context` beside each other. Bring `harness/guidance/fidelity_outputs_spec.py` and `space/kanban/kanban_tools_spec.py` up to date with that. Check every other fidelity that offers drawio offers whiteboard under the same chip, and list any that does not. | `cdd_guidance/practices/ux/`, the two specs named |
| Widget | **Java is removed everywhere.** `JavaCleanEngineeringModel`, `JAVA` in `code_body.py`, `.java` in the Clean Engineering and DDD file patterns, `is_spec_file`'s Java names, Java templates, examples, fixtures, docs and specs: deleted with every caller in one pass. Languages are Python, TypeScript and JavaScript. | `cdd_guidance/practices/clean_engineering/`, `cdd_guidance/practices/ddd/` |
| Cog | **JavaScript story tests level with TypeScript, tested on the graph through shared behaviours.** JavaScript reads and writes what TypeScript does: shared step files, screen specs, domain and server tier files, examples, its own template and step library, offered at acceptance_tests. The person's rule for the tests: most tests are on the graph the model creates, written once as shared behaviours and reused for each language. So write the behaviours once (a shared set of examples that takes a language and its fixture and asserts on the graph's nodes and edges and on the trip back), run them for Python, TypeScript and JavaScript, and keep per-language specs only for what one language alone does. Move existing per-language duplicates of the same behaviour into the shared set as you go; report what you moved and what remains. | `cdd_guidance/practices/stories/model/` and its specs, `harness/graph/` |

Anvil and Cog both touch Stories code formats: Cog owns reading and writing a file's text, Anvil owns where the rendered text is saved. Each asks the other through "needed from" rather than editing across that line.

## Fourth answers from the person (2026-11-21), and the fifth wave

**A render reshapes an existing file and loses nothing.** This replaces the "kept whole" rule of the fourth wave. In the person's words: "render should match files to the new shape, but existing code, comments, whatever exists only in one shape must be preserved. For example we add an operation to markdown model or diagram on a class; we re-render that class that already had code in it; you need to put the code back into that class; new operation is empty; re-render must not ever remove what is already there, only exception is if classes or methods have been refactored away; even then existing code must be re-allocated afterwards. This means we need an AI pass to migrate inner details of code formats after render has made its changes to ensure nothing is lost."

What that asks of the Render action and each format:
- A render onto a file already there writes the new shape (classes, operations, properties, steps, specs as the source now has them) and puts back, in the member it belongs to, everything only the existing file holds: bodies, comments, imports, helpers, decorators, anything between members.
- A member the source has and the file lacks is added empty. A member the file has and the source lacks is not deleted: its text is kept in the file, set apart and marked as no longer in the model, with where it came from.
- Nothing is ever dropped silently. After writing, the render checks that every line of the old file that carried content is in the new file, and fails loudly naming any it cannot find.
- The render's result lists what needs migrating: each kept member no longer in the model, and each new member that may be where its code now belongs (a rename or a move looks like one removed and one added). The instructions the Render action hands the agent (place_rendered) tell it to do that migration as its next step: move each kept body into the member that replaced it, then delete the set-apart text only once its content is placed, and say what it moved.
- The same holds for documents and drawings where one format holds what the other does not (descriptions, notes, layout).

**A bounded context's file links its aggregates to the domain model** (answer 1): `bounded-context.md` names each aggregate as a markdown link to its heading in the domain model, the template and generate guidance say so, the formats write and keep the link, and the Files app's callout opens the aggregate in place; Diagnose's 13 edges with no callout on the Bookshop then report nothing.
