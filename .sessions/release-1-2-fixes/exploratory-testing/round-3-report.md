# Round 3 report — every fidelity of every practice in every format

Asked for on 2026-11-19. Eight robots, two passes, one product (the Bookshop). The first pass ran on build 4d47fdf8e, the second on aa23b0968, both on `release-1-2-fixes`. The charters are in `charters.md`, the reports in `defects/r3-*.md`: 68 files, 62 defects and 6 questions. Nothing was fixed in this round.

## The six things asked, and what was found

| Asked | Answer | Main evidence |
|---|---|---|
| 1. An artifact is generated for every stage, practice and format | No. A file exists for most pairs, but several formats are only reached by hand or not at all. | Stories thin slice has no drawio and no template (r3-sparky-01); scenarios and acceptance tests in code are written by hand, since the render does not parse (r3-sparky-06, 07, 11); DDD and Clean Engineering code renders return one text and save nothing (r3-bolt-06); UX `claude_design` answers `{}` and JavaScript has no adapter (r3-gizmo-03, 05); BDD Java is offered and nothing reads it (r3-rivet-01). |
| 2. It renders to every other format | No. No practice has a fidelity whose content survives every trip. | UX IA between drawio and markdown empties the other file (r3-gizmo-01); a second class model takes the first one's class names (r3-widget-04); BDD bodies come back commented out, wrapped again on each trip (r3-rivet-07); an observation moves below its nested state (r3-rivet-03); the story map, the bounded-context map and both models lose descriptions, links, invariants and integrations through a drawing (r3-sparky-02, r3-bolt-03, widget-08, widget-20). |
| 3. It is displayed in every format, with callouts for links to other files and practices | Every file opens. Reading and callouts fail. | Rendered markdown drops all text in angle brackets, so stereotypes vanish (r3-pixel-01); a link in the rendered view does nothing, and the source view shows 14 of 28 link callouts (r3-pixel-03, 04); story tests in code show no callouts (r3-pixel-05); 15 of 102 practice files are in no list (r3-pixel-06, r3-lens-02). |
| 4. It becomes the correct graph, in and across practices | Inside a practice, mostly for Stories, BDD and Clean Engineering code. Across practices, no. | No edge reaches DDD or UX from another practice. Step's domain term to DDD class: 0 of 43. DDD model to code: 0 of 12. Clean Engineering model to code: 0 of 8. BDD describe to class: 0 of 6. UX: no node at all (r3-gizmo-06). Calls are matched by name, so 15 of 31 BDD links and 51 of 57 story-test links are wrong (r3-cog-01, r3-widget-09). One class is up to eight unjoined nodes (r3-cog-05). Refreshing unchanged files changes the graph (r3-cog-02). |
| 5. The graph tree is viewed properly | Mostly, for what the graph holds. | Stories 83 of 83 nodes shown with 6 doubled; DDD 41 of 44; Clean Engineering 515 of 522; BDD 62 of 62; UX none. Selecting a module, package or aggregate fails with a 500 (r3-lens-01). |
| 6. Files related to a node are viewed properly, with trees | Partly. Code, DDD and BDD nodes open their one file at the right lines. | Markdown stories and scenarios are marked at the wrong lines (r3-lens-03, 04); a file changed on disk keeps its old lines (r3-lens-07); a relationship's member opens only the file that holds it (r3-lens-08). The page draws no tree per related file: each opened file has its own fold outline. |

## Reports by robot

| Robot | Covered | Defects | Questions | Worst |
|---|---|---|---|---|
| Sparky | Stories | 10 | 1 | No Stories format passes validate, markdown written to the template included (r3-sparky-04) |
| Bolt | DDD | 7 | 0 | Most of the DDD model never reaches the graph (r3-bolt-01) |
| Gizmo | UX | 4 | 2 | IA render between its two formats empties the other file (r3-gizmo-01) |
| Widget | Clean Engineering | 10 | 0 | A second model rendered to markdown takes the first model's class names (r3-widget-04) |
| Rivet | BDD | 10 | 1 | Python to TypeScript and back leaves every body commented out (r3-rivet-07) |
| Cog | Graph across practices | 4 | 1 | Refreshing unchanged Stories files detaches, doubles or drops scenarios (r3-cog-02) |
| Pixel | Display | 7 | 2 | Rendered markdown drops text in angle brackets (r3-pixel-01) |
| Lens | Graph tree and node files | 9 | 0 | Folder nodes fail with NamedPathNotFoundError, a regression from the pixel-08 fix (r3-lens-01) |

## Confirmed by a second robot

Cog and Lens saw these first-pass reports again on the combined project: r3-bolt-01, r3-bolt-05, r3-gizmo-06, r3-widget-08, r3-widget-09, r3-widget-10, r3-rivet-03, r3-rivet-09, r3-sparky-03, r3-sparky-05, r3-sparky-08, r3-sparky-09. The other reports rest on one robot's run.

## Earlier defects checked again

- Fixed and holding: widget-04 (the story map keeps its title through a drawing).
- Still failing: widget-06 (a thin slice render replaces the story map's drawing), widget-08, widget-15, widget-19, widget-20.
- A regression from this session's own fixes: r3-lens-01, from the pixel-08 fix.

## Themes

1. **The graph is per practice and per file, joined by name.** Nothing says that the Order of the domain model, the Order class, and the Order a step underlines are one thing, and a call is linked to every operation of that name. This is behind points 4, 5 and 6.
2. **Each format holds less than markdown, and the trip back writes over the markdown.** A drawing, a whiteboard or code cannot hold prose, invariants or links, and the render saves the smaller result over the fuller file.
3. **Templates and rules disagree.** A file written to the template fails validate in Stories scenarios and the DDD model (r3-sparky-04, r3-bolt-02), and validate says "passed" where it read no node (r3-rivet-02, r3-widget-08).
4. **Which files a fidelity owns.** Story tests under an epic with no sub-epic, `bounded-context.md` files, JSON maps and front-end views are no fidelity's files, so they are in no list and no tree.
5. **The new rendered view** of the Files app (aa23b0968) is the default for markdown and accounts for six of Pixel's nine reports.

## Decisions for the person

1. Is a link in the rendered view meant to do nothing (r3-pixel-03)? The module card says so; the request for callouts says otherwise.
2. Is a step's domain term meant to be an edge to the DDD class (r3-sparky-05), and is UX meant to be in the graph at all (r3-gizmo-06)?
3. Is one class in several practices, languages and folders one node or several joined ones (r3-cog-05)?
4. What should a relationship's member open: its own file, or the file that holds the relationship (r3-lens-08)?
5. What is a mockup rendered to Claude Design meant to answer (r3-gizmo-03), and is a finished spec meant to come back from markdown as signatures only (r3-rivet-11)?
6. Is the HTML mockup meant to run its script in the Files app (r3-pixel-08)?

### Answers from the person, 2026-11-20

1. **Links and callouts in the Files app (r3-pixel-03, 04, 05).** Rendered and Source both show callouts and both follow links. Which callouts show follows the file view's filters: the practices chosen and the graph. A callout is traversable as the graph tree is: from the story map a person opens a scenario, then what it observes, then an operation of the class, each in place.
2. **Domain terms and UX (r3-sparky-05, r3-gizmo-06).** A step's linked domain term is an edge to the DDD class. UX joins the graph.
3. **One class in several practices (r3-cog-05).** Several nodes with edges between them. A DDD entity is a kind of class, so the DDD node has an "is a" edge to the Clean Engineering class node of the same file, and selecting the DDD node reveals the Clean Engineering node with its details. A module relates to an aggregate or a bounded context the same way: an ordinary edge, though both come from one file. (Read by the supervisor as two nodes joined by "is a", not one merged node; to confirm.)
4. **What a relationship's member opens (r3-lens-08).** Selecting the parent shows the parent in its file, where its children can be opened in place. Selecting the child shows only the child, in the child's own file: selecting `authorise` under `check_out`'s invokes group shows `payment.py` at `authorise`, not `cart.py`.

## Not reached

Publishing a whiteboard to a board in Claude; a real Claude Design canvas; running the generated Vitest specs and story tests; the sketch, json, java and javascript adapters as formats in their own right; two callers at once; LERN overlays; drag and drop; the Claude desktop app's own chat bar.

## Where things are

- Sandboxes: `C:\dev\_et\round3\<robot>`; the combined project: `C:\dev\_et\round3\combined\work`.
- Screenshots: `C:\dev\_et\round3\pixel\shots` and `C:\dev\_et\round3\lens\shots`.

## What was fixed (2026-11-20)

Two waves of robots closed the gaps, test first, each in its own files; the lead committed after each report. Commits 88c9f6d3a to 1194888e0 on `release-1-2-fixes`.

| Defect | State | Note |
|---|---|---|
| r3-sparky-01, widget-06 | fixed | A thin slice is drawn as its increments and saved as its own drawing |
| r3-sparky-02 | fixed | A story map back from a drawing keeps descriptions, story links and scope |
| r3-sparky-03, 05, 08, 09 | fixed | One Background per story; a step's domain term is an edge to the DDD class; story tests keep steps, invokes edges and examples; a step invokes only code its file reaches |
| r3-sparky-04 | part | The example-file rule no longer runs on markdown; every Then needing an Example waits on the person |
| r3-sparky-06 | fixed | Scenarios rendered to Python or TypeScript parse |
| r3-sparky-07 | part | A code render holds only its own stories; where it is saved waits on the person |
| r3-sparky-10 | part | A story test validated alone takes its place from the map |
| r3-sparky-11 | part | Schema text only; no acceptance-test template per language |
| widget-19 | part | An outline's examples survive code; front matter, story type and term links do not |
| r3-bolt-01, 02, 03, 05 | fixed | Contexts, mappings, events and dependencies reach the graph; a model after the template validates; arrows read back |
| widget-20 | fixed | Prose, invariants, events and integrations survive a drawing written over its markdown; a drawing with no markdown beside it has nothing to take them from |
| r3-bolt-04 | not fixed | The drawio model still draws no context or aggregate container |
| r3-bolt-06 | waits on the person | Whether a code render saves files; today it answers content and the declared paths |
| r3-bolt-07, r3-widget-07 | part | Type spellings and names are right; properties, imports and super calls are not |
| r3-gizmo-01 | fixed | A render between the IA drawing and the UX context leaves the other file alone |
| r3-gizmo-02, 04 | part | Stories, terms and controls read back; descriptions, states and interactions are not drawn, which waits on the person |
| r3-gizmo-05 | part | Rendering a view is refused by name; whether views render between languages waits on the person |
| r3-gizmo-06 | fixed | UX is in the graph |
| r3-widget-01 | part | The modules drawing is saved in the root `.context`; the trip back still writes one `modules.md` |
| r3-widget-02, 03, 04, 06, 08, 09, 10, widget-08 | fixed | Module cards, class models and the graph reading |
| r3-widget-05 | fixed | A `.md` path is read as markdown |
| r3-rivet-01 | fixed by removal | Java is no longer offered for BDD specs |
| r3-rivet-02 | fixed | Validate names each path that gave the graph no node |
| r3-rivet-03 to 07, 09, 10 | fixed | Spec trips and BDD graph links |
| r3-rivet-08 | part | A graph render answers content and the declared path; it no longer saves `graph.md` |
| r3-cog-01, 02, 04 | fixed | Links by import; refresh leaves the graph as loaded; a story off the map is reported |
| r3-cog-03 | part | A whole load reads code story tests; DDD roots' own code is not reached |
| r3-cog-05 | fixed | Document and code nodes of one class both stay, joined by `isA` and `implements`; aggregate and context to module |
| r3-pixel-01 to 05, 07, 09 | fixed | Rendered and Source views show callouts and follow links |
| r3-pixel-06, r3-lens-02 | fixed in the declarations | Not checked in the Files app |
| r3-lens-01, 03 to 08 | fixed | Graph view selection, lines, filters |
| r3-lens-09 | not fixed | Tree entries that cannot be told apart |
| r3-gizmo-03, r3-rivet-11, r3-pixel-08 | wait on the person | Unanswered questions |

### What the fixes broke, and how it was caught

The unit tier, run after each wave, caught three knock-on breaks, each fixed before the next run:
1. Linking a call only through what a file imports dropped the invokes edges of this repository's own story tests (5 examples) and of operations whose parameter is annotated with a class the file does not import (2 examples). The link now follows the class the file built the receiver as, an annotation naming a class of the file's own folder, and, for a receiver of no known class, the one class in the caller's file that declares the operation.
2. The new file declarations moved a fidelity's proposed root up one folder (6 examples) and put two examples over the 100 ms budget.
3. A renamed scenario was still listed under its old name in a server-tier spec.

### Known limits of the fixes

- A call through a field typed only by its constructor assignment, or a local typed only by an annotated return, still gets no edge.
- A step's id still carries its line number, so a step is not found again after its file changes.
- Stories and BDD each have their own class that follows a file's imports.
- Which callouts show is worked out on the page, not in Python, against the project's own rule for web access to the domain.
- In the Source view a link opens on Ctrl-press and leaves an editor error in the console; checked by hand only.
- Several tests were not seen failing before their fix, because another robot's half-made edit broke imports at that moment: Rivet's for r3-rivet-03, 06, 07, Gizmo's drawio read-back, Cog's for r3-sparky-08, Anvil's render-level examples for the thin slice and the modules drawing.
- No robot ran the metrics gate, and most did not call generate or validate through the cdd server, whose answers were too long to read whole.

### New decisions for the person

1. Does a render to Python or TypeScript save its files at the fidelity's declared paths, or answer content for the agent to save (r3-bolt-06, r3-sparky-07)?
2. Does every Then have to observe an Example (r3-sparky-04)? Scenarios written to the template fail the rule.
3. Is Java removed from BDD specs, or supported (r3-rivet-01)?
4. Should the IA drawing show descriptions, content types and notes, and a mockup's drawing its states and interactions (r3-gizmo-02, 04)?
5. Does a link to a heading that is not there get a callout saying so? It replaces an older scenario that said it carries none (r3-pixel-04).
6. Do front-end views render between TypeScript and JavaScript (r3-gizmo-05)?

### Second answers from the person, 2026-11-20

- **Callout filtering** is done in Python by the same filter code that narrows the knowledge graph. Every application gets all its business logic from Python, through TypeScript, the cdd server and the Python adapter, with no exception.
- **1** (does a code render save its files): not answered.
- **2**: a Then must observe an Example only where a domain model or a class model has been written for that area of the story graph. Where none is written, scenarios may link to terms they come up with, and the graph need not connect them.
- **3**: Java stays removed, to be made when it is needed. Specs are Python, TypeScript or JavaScript.
- **4**: a mockup's whiteboard needs only a way to associate screens and widgets with stories, scenarios and steps.
- **5**: yes. More widely, a failure in display, in a render or generate action, or in the session's roots shows a Fix button that lists the most common causes and sends them to the AI to fix.
- **6**: yes. And the context viewer gets a Diagnose and align button: it goes through the graph and the selected stages, fidelities and formats, finds the gaps, then brings the formats in step; failures can be fixed. It checks that the graphs of the formats agree and that the callouts match.

### Tier results on the fixed code (2026-11-20, commit 1194888e0)

- **Unit:** 382 of 382 files, none over the 100 ms budget.
- **Heavy:** 62 of 63 files. The one failure is the OSS portal pattern's fixture copy, whose paths are too long inside the tier's worktree; that pattern is left out of this work.
- **E2E, without agent specs:** 7 of 10 files, 270 of 275 Playwright tests.
  - Four Playwright tests expected five tabs for the story map fidelity and found six, the thin slice's whiteboard being declared now. The spec and its scenario are updated and its 13 tests pass.
  - `review-files-in-files-app.story.ui_e2e_spec.py` (pixel-09) and the viewer's line 14 test (pixel-10) failed before this session and still do.
  - `prompt_queue_plugin_e2e_spec.py` fails all 6: it cannot start a headless Claude Code chat on this machine.
- The whole e2e tier was not run again after the tab fix.

## Third wave: the second answers built (2026-11-20, commit 5c3b22e83)

| Answer | Robot | What is built | What is left |
|---|---|---|---|
| Callout filtering in Python | Pixel | `space/session/file_view_filter.py` *FileViewFilter* decides which callouts a file shows with the graph's own `Filter`; the page sends its filters with `session.file` and draws what comes back; the page's `shows` rule is deleted. Seen on a real run and in e2e. | Other rules the file view still decides in TypeScript, found and not moved: which line of a step carries a callout, a callout's title, which fold-outs open, which files open rendered, a second resolving of a link's path, and the file list's `filesShown`, `rootFilesShown`, `listedBy`, `emptyReason`. |
| A Then observes an Example only where a model is written | Cog | New graph rule `then-observes-an-example`. A story's area is the stories under its sub-epic or epic; a model is written for it when a step or example of the area has an edge to a domain model or class model node. A term link to a missing model raises nothing. | On this repository 643 Thens in modelled areas observe no Example. An example that demonstrates a DDD class is still reported when Clean Engineering is loaded. |
| Java removed; Python, TypeScript or JavaScript | Cog | Stories' Java story-test format and every Java mention for specs removed. JavaScript offered for BDD in all three fidelities and for Stories scenarios and acceptance tests. | JavaScript story tests read only the story test file: no shared steps, screen specs, template or step library. Clean Engineering still reads Java production code. |
| Mockup associates screens and controls with stories, scenarios, steps | Gizmo | Controls carry the associations as screens do; the drawing and a new whiteboard show them and read them back; the graph joins them by link target. | The drawing and whiteboard are not formats a person picks at mockup on the board: offering them fails two specs outside UX (drawio outputs must sit in `.context`; the board expects code and canvas for mockup). |
| Views between TypeScript and JavaScript | Gizmo | Both ways; a view with an enum, namespace or constructor parameter property is refused by name. Compared with the TypeScript compiler on 700 files: 674 matched, 26 refused, none differed. | Not run through the cdd server. |
| Fix button on failures | Lens | The Files app keeps each failure in a band with Fix; Fix lists the common causes Python holds for that kind (`tools/error_display/failure.py`) and sends the debug-session fix command to the chat that opened the page. | The board's fidelity outputs raise no such failure yet. No live Claude chat took the command; a stand-in chat did. A graph view failure was not made for real. |
| Diagnose and align | Anvil | `session.diagnose_alignment` and `session.align_formats`, and the button in the Files app. Missing format files, formats whose graph readings differ, callouts that match no edge. Align renders from the format that holds more; formats that each hold something the other lacks wait for the person. | Callout matching is proven only by the real run. The file list does not show newly rendered files until it lists again. A story deleted on purpose from one format is restored from the fuller one. |

Unit tier after the wave: 384 of 386 files, then 386 of 386 after two expectations were brought up to date (the board's tool names gained the two alignment tools; the catalog spec now names the Diagnose utility's own page).

New decisions for the person:
1. Still open: does a render to Python or TypeScript save its files, or answer content?
2. Should the mockup's drawing and whiteboard be formats a person picks on the board, saved under the epic's `.context`?
3. Does Clean Engineering keep reading Java production code?
4. Are edges between bounded-context files and the domain model expected to carry a link (13 reported on the Bookshop)?
5. Should JavaScript story tests be brought level with TypeScript (shared steps, screen specs, template, step library)?
