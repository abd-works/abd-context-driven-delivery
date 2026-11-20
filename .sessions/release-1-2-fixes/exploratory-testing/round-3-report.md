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

## Not reached

Publishing a whiteboard to a board in Claude; a real Claude Design canvas; running the generated Vitest specs and story tests; the sketch, json, java and javascript adapters as formats in their own right; two callers at once; LERN overlays; drag and drop; the Claude desktop app's own chat bar.

## Where things are

- Sandboxes: `C:\dev\_et\round3\<robot>`; the combined project: `C:\dev\_et\round3\combined\work`.
- Screenshots: `C:\dev\_et\round3\pixel\shots` and `C:\dev\_et\round3\lens\shots`.
