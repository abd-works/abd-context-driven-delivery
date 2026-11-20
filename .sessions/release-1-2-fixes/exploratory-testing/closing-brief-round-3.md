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
