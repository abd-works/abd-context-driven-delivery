# Defect themes by wave of testing — release 1.2 (2026-11-21)

Each wave's defects are grouped into themes. Sources: the 156 files in [defects/](defects/), [final-report.md](final-report.md) and [round-3-report.md](round-3-report.md). Root causes come from the defect reports and the fixes' commits; they were not checked again against each defect file for this report. Rounds 1 and 2 shared one defect area, so which of the two a defect belongs to is read from the charters and is approximate for a few.

## Classification tags

| Tag | Meaning |
|---|---|
| `concurrency` | Two callers or processes on one file or resource |
| `unchecked-input` | A name, path or argument taken as given |
| `data-loss` | Content a person wrote is removed or written over |
| `lossy-format-trip` | A render to another format and back returns less than went in |
| `stale-state` | A record outlives the thing it describes |
| `false-success` | A call answers success while doing less than asked, or nothing |
| `raw-error` | A failure reaches the person as a traceback or a misleading message |
| `name-matching` | Things are joined by a shared name instead of by what they are |
| `rule-template-mismatch` | A rule, a template and an adapter disagree about the same file |
| `undeclared-output` | A file or format no fidelity owns, so no list, tree or render reaches it |
| `display` | The Files app or board shows the content wrongly |
| `regression` | A fix in this session broke something that worked |

**Caught by** names the testing layer that found the defect: exploratory testing, or a tier of the automated tests (unit, which holds the BDD specs and the domain and server tiers of the story tests; heavy; e2e, which holds the browser story tests). Every defect of waves 1 to 4 was found by exploratory testing, which is why those waves were run: no automated layer had caught them.

## Modules sorted by defects

The counts are the defects named in the themes below: 146, of which 132 came from the four exploratory waves and 14 were found while fixing. The defect area holds 156 files; the other ten are questions and reports the themes do not name. A defect whose theme names several modules is counted once for each, so this column adds up to more than 146.

| Module | Defects | Wave 1 | Wave 2 | Wave 3 | Wave 4 | Wave 5 | Mostly |
|---|---|---|---|---|---|---|---|
| `cdd_guidance/practices/stories` | 29 | 0 | 5 | 11 | 7 | 6 | graph reading, trips between formats |
| `space/session` | 26 | 8 | 2 | 0 | 13 | 3 | graph view, file lists, output roots |
| `harness/graph` | 20 | 0 | 2 | 12 | 5 | 1 | joins made by a shared name |
| `space/kanban` (with its app) | 19 | 13 | 2 | 0 | 0 | 4 | ticket names, worktrees, close |
| `harness/files_app` (with its app) | 19 | 4 | 0 | 0 | 13 | 2 | rendered view, callouts, selection |
| `cdd_guidance/practices/clean_engineering` | 19 | 0 | 5 | 12 | 2 | 0 | class model in markdown, drawings |
| `cdd_guidance/actions` | 17 | 12 | 0 | 1 | 0 | 4 | render's saved file, quiet success |
| `harness/installation` | 16 | 16 | 0 | 0 | 0 | 0 | install record, two installs at once |
| `cdd_guidance/practices/ddd` | 15 | 0 | 3 | 8 | 4 | 0 | model missing from the graph, drawing |
| `harness/diagnostics` | 14 | 11 | 0 | 0 | 0 | 3 | record of test runs |
| `cdd_guidance/practices/bdd` | 13 | 0 | 0 | 10 | 2 | 1 | spec trips between formats |
| `scripts` | 12 | 12 | 0 | 0 | 0 | 0 | install scripts, the test runner |
| `space/repo` | 11 | 11 | 0 | 0 | 0 | 0 | worktrees against git's own list |
| `tools/prompt_queue` | 10 | 10 | 0 | 0 | 0 | 0 | two writers, unchecked input |
| `cdd_guidance/practices/ux` | 10 | 0 | 0 | 6 | 4 | 0 | formats with no adapter, drawings |
| `harness/guidance`, `harness/guidance_actions` | 3 | 3 | 0 | 0 | 0 | 0 | guidance argument matching |
| `story_tests` | 3 | 0 | 2 | 0 | 0 | 1 | browser tests older than the page |
| `harness/mcp` | 2 | 2 | 0 | 0 | 0 | 0 | mods copied by two installs |
| `cdd_guidance/desktop_walk` | 1 | 0 | 0 | 0 | 0 | 1 | the walk cannot reach the Claude app |

By area: the five practices together hold 86, `space` 56, `harness` 74, `cdd_guidance/actions` 17, `scripts` and `tools` 22, the story tests and the desktop walk 4.

## Testing tier or type by defects found

Each defect is counted once here, under what found it.

| Found by | Type | Defects | Share | What it found |
|---|---|---|---|---|
| Exploratory, round 1 (six tester robots) | exploratory | 57 | 39% | tools and workflows at their edges |
| Exploratory, round 3 first pass | exploratory | 44 | 30% | every fidelity, practice and format |
| Exploratory, round 3 second pass | exploratory | 22 | 15% | the combined graph and its display |
| Exploratory, round 2 | exploratory | 9 | 6% | areas round 1 missed |
| Unit tier (BDD specs; story tests, domain tier) | automated | 6 | 4% | regressions from fixes, a fault shared by four languages, a note lost from a drawing |
| The person, on the board's report | exploratory | 2 | 1% | false findings in a validation report |
| The person's review of the code | review | 2 | 1% | business rules decided on the page |
| Heavy tier (install health probe, server health) | automated | 2 | 1% | answers a fix changed on purpose |
| E2E tier (browser story test) | automated | 1 | 1% | a test that fails only inside the tier |
| Exploratory, first real run of the desktop walk | exploratory | 1 | 1% | the walk cannot reach the Claude app |
| Story tests, server tier | automated | 0 | 0% | — |
| Story tests, browser tier, on a product defect | automated | 0 | 0% | — |

| Type | Defects | Share |
|---|---|---|
| Exploratory (robots and the person) | 135 | 92% |
| Automated tiers | 9 | 6% |
| Review | 2 | 1% |

All nine defects the automated tiers found were found while fixing: before the fixes started, the tiers were green on every one of the 132 defects the robots then found.

## Defects by the testing layer that should have caught them

Exploratory testing is left out: each defect is placed under the cheapest automated layer that could have failed on it before a person or a robot met it. The placing is my judgment per theme, from what the defect needs in order to show: a rule or one object alone (BDD spec), a story's behaviour on the domain objects (story test, domain tier), the same through the cdd server (story test, server tier), real git, processes or an installer (heavy tier), or a real browser (e2e tier). The layers are ordered by the number of defects.

| Layer that should have caught it | Tier | Defects | Share |
|---|---|---|---|
| Story tests, domain tier | unit | 49 | 34% |
| BDD specs beside the code | unit | 41 | 28% |
| Heavy specs (real git, processes, the installer, whole-project graph loads) | heavy | 28 | 19% |
| Story tests, server tier | unit | 13 | 9% |
| Browser story tests | e2e | 13 | 9% |
| No test layer: a code review or a Clean Engineering rule | — | 2 | 1% |

The unit tier should have caught 103 of the 146 (71%), and it caught 6.

### Story tests, domain tier — 49

| Defect theme | Wave | Defects | The test that was missing |
|---|---|---|---|
| Ticket name made from a title | 1 | 5 | a ticket created from an empty, taken or too-long title is refused |
| Render saves over the wrong file | 1 | 5 | a render of one path leaves every other file of the folder as it was |
| Spec trips between formats | 3 | 5 | a spec rendered to each format and back is the same spec |
| Class model in markdown (trips, names kept between renders) | 3 | 3 | two models rendered in turn each keep their own classes |
| Calls that answer success and do less | 1 | 3 | validate, document and output roots refuse empty or unusable input |
| A trip through another format loses prose | 2 | 3 | a file rendered to each format and back keeps its prose |
| Scenarios rendered to code | 3 | 3 | an outline renders to code that parses, one file per story |
| Model rendered to code | 3 | 3 | a code render is saved at the fidelity's paths in the language's types |
| Modules drawing and whiteboard | 3 | 3 | a module card through a drawing keeps its language and constraint |
| Three defects in every language | 5 | 3 | one shared behaviour run for each language |
| Board and graph view on one bad file | 2 | 2 | a board with one unreadable session still shows the others |
| Domain model drawing | 3 | 2 | a drawing read back keeps its arrows and containers |
| UX drawings drop what they show | 3 | 2 | a drawing read back keeps every label it shows |
| Files no fidelity owns | 4 | 2 | every practice file of a project is declared by a fidelity |
| Thin slice has no format of its own | 3 | 1 | every file generate names can be chosen and rendered |
| Story map back from a drawing | 3 | 1 | a story map through a drawing keeps descriptions, links and scope |
| IA render empties the other file | 3 | 1 | a render to one format leaves the other format's file whole |
| Validate passes a file it read nothing from | 3 | 1 | validate reports a path that gave the graph no node |
| False findings: a saved report older than its rule | 5 | 1 | a report saved before a rule changed is marked out of date |

### BDD specs beside the code — 41

| Defect theme | Wave | Defects | The test that was missing |
|---|---|---|---|
| Record of test runs describes the wrong run | 1 | 7 | a record whose commit, process or claim is no longer live is not trusted |
| Stories graph reading | 3 | 5 | a step invokes only the operation of its own language and class |
| Damaged or wrongly shaped state file | 1 | 4 | an unreadable file is refused by name, never read as empty |
| Prompt queue keeps input it should refuse | 1 | 4 | a blank card, an unknown step state and a chat id with a path are refused |
| BDD realization and graph links | 3 | 3 | a rule's failing and repaired example in each quoting style |
| Graph leaves out what it cannot place | 2 | 2 | a file that gives the graph no node raises a violation |
| DDD model missing from the graph | 3 | 2 | a context, integration and event each become a node |
| UX formats that cannot be rendered | 3 | 2 | every format a fidelity offers has an adapter |
| Code graph joined by name | 3 | 2 | a call joins the one operation its receiver's class has |
| New repository's ignore lines | 1 | 1 | a new repository's ignore file holds only the lines a new project needs |
| Scenarios after the template fail validate | 3 | 1 | each template passes its own fidelity's rules |
| Domain model after the template fails validate | 3 | 1 | each template passes its own fidelity's rules |
| UX is not in the graph | 3 | 1 | every practice gives the graph at least one node |
| Class model in markdown gives the graph no class | 3 | 1 | a markdown model's classes are graph nodes |
| Java offered and never read | 3 | 1 | every format a fidelity offers has an adapter |
| Linking calls by import dropped real edges | 5 | 1 | caught here, by seven examples |
| Changed declarations moved a proposed root | 5 | 1 | caught here |
| A render removed a person's note from a drawing | 5 | 1 | caught here, while the spec was being restructured |
| False findings: "once" in a name read as a one-time task | 5 | 1 | a rule's failing and repaired example pair |

### Heavy specs — 28

| Defect theme | Wave | Defects | The test that was missing |
|---|---|---|---|
| Install record and install target | 1 | 6 | a second install, a wrong IDE name and a bad path against a real installer |
| Worktree outlives its ticket, or the ticket its worktree | 1 | 6 | activate, delete and archive against real git after a folder or branch is removed by hand |
| Refresh and whole loads change the graph | 4 | 3 | a whole project loaded, refreshed unchanged, and compared |
| Prompt queue loses changes with two writers | 1 | 2 | two processes changing one queue file |
| Two installs at the same moment | 1 | 2 | two installer processes at once |
| Installer refresh and release version | 1 | 2 | `--self` and install-latest on a real install |
| Close does its steps in the wrong order | 1 | 2 | a close whose merge conflicts, in real git |
| No edge crosses a practice | 4 | 2 | one project holding all five practices, its links counted |
| Saved code renders turned the install probe red; health report's new question | 5 | 2 | caught here |
| A spec file that ran no examples counted as passed | 1 | 1 | the test runner on a file that runs nothing |

### Story tests, server tier — 13

| Defect theme | Wave | Defects | The test that was missing |
|---|---|---|---|
| Graph view selection fails or marks the wrong lines | 4 | 4 | each kind of node asked for its lines through the cdd server |
| Guidance argument matching | 1 | 3 | a misspelled slug and a rule's name sent through the published schema |
| Files app: a deleted file, a non-ASCII name | 1 | 2 | the file list and a read through the cdd server |
| Graph view filters | 4 | 2 | no selection and an empty selection answer differently |
| Graph tree entries and relationship members | 4 | 2 | a member answers its own source; same-named entries differ |

### Browser story tests — 13

| Defect theme | Wave | Defects | The test that was missing |
|---|---|---|---|
| Rendered markdown view | 4 | 4 | each practice's file opened in the rendered view |
| Links and callouts | 4 | 3 | a link pressed and a callout shown, in both views and in code |
| Files app: a huge file, a missing project folder | 1 | 2 | the page opened on each |
| Browser tests older than the page | 2 | 2 | the tier kept green as the page changed |
| Graph view browser test fails only inside the tier | 5 | 1 | caught here |
| The chat bar cannot be walked from inside the Claude app | 5 | 1 | one real run of the walk's first step when it was built |

### No test layer — 2

| Defect theme | Wave | Defects | What would have caught it |
|---|---|---|---|
| Business rules decided on the page | 5 | 2 | a review, or a Clean Engineering rule that fails a page deciding what Python should |

## Wave 1 — Round 1: six robots explore the tools and workflows

| Defect theme | Module(s) | Description | Root cause | Classification | Practice | Stage | Format | Caught by |
|---|---|---|---|---|---|---|---|---|
| Prompt queue loses changes with two writers (sparky-01, 02) | `tools/prompt_queue`, `harness/installation` | Two processes changing one chat's queue each answered success, and one change was gone; with both lanes' servers on one chat only 43 of 90 adds were kept. A read that met another write saw an empty queue and saved it. | The queue was read, changed and written with no lock across processes, and `JsonFile.read` returned empty for a half-written file. | `concurrency`, `data-loss`, `false-success` | — | — | json | exploratory (tester robot) |
| Damaged or wrongly shaped state file (sparky-03, 04; rivet-06, 07) | `tools/prompt_queue`, `harness/diagnostics`, `harness/installation` | A truncated or hand-edited queue file or record of test runs was read as empty and written over, or stopped every call with a `TypeError`. The person lost the file's content or got a traceback naming no file. | `JsonFile.read` treated unreadable as empty, and no reader checked the shape of valid JSON before using it. | `data-loss`, `raw-error` | — | — | json | exploratory (tester robot) |
| Prompt queue keeps input it should refuse (sparky-05, 07, 08, 09) | `tools/prompt_queue` | A blank edit left an empty card, a step state outside the three allowed was kept, a card stood in two robots' queues, and a chat id such as `..\escape-chat` wrote a queue file outside the chats folder. | Arguments went straight into the stored queue and into a folder path with no check. | `unchecked-input` | — | — | — | exploratory (tester robot) |
| Install record and install target (bolt-01, 02, 03, 04, 06, 11) | `harness/installation`, `scripts` | An install into a second folder made the first folder's install unknown, a lowercase or unknown IDE name installed the Cursor layout, and a file or an empty string was accepted as the install path. A stopped install left files that clean could not find. | One shared install record, written at the end and holding paths as typed; the IDE name fell through to a default layout. | `unchecked-input`, `stale-state` | — | — | — | exploratory (tester robot) |
| Two installs at the same moment (bolt-12, 13) | `harness/installation`, `harness/mcp` | Two installs from main and a worktree, or two into one folder, failed one of them with a `WinError` or a `FileNotFoundError` in clean. | No lock around an install or around copying the mods into the shared cdd home. | `concurrency`, `raw-error` | — | — | — | exploratory (tester robot) |
| Installer refresh and release version (bolt-14, 16) | `harness/installation`, `scripts` | `install.py --self`, described as refreshing only the installer's own commands, removed every skill, rule and adapter. Install-latest on a checkout past the newest release put the version number back. | The `--self` deployment cleaned by the whole record; the version match overwrote a newer committed number. | `data-loss`, `false-success` | — | — | — | exploratory (tester robot) |
| New repository's ignore lines (bolt-05) | `space/repo` | `make_repository` copied every ignore line of the CDD checkout, so the first commit left out the person's own files. | `NewRepository.write_ignores` copied CDD's own ignore file instead of writing the few lines a new project needs. | `data-loss` | — | — | — | exploratory (tester robot) |
| Ticket name made from a title (gizmo-03, 04, 05, 06, 13) | `space/kanban` | A title with no Latin letter made a ticket named `.sessions`, two long titles shared one worktree folder, an existing name retitled that ticket, and a long title failed with `WinError 206`. A backlog idea with a taken title overwrote the first. | The name derived from the title was never checked for being empty, taken or too long before folders were made from it. | `unchecked-input`, `data-loss`, `raw-error` | — | — | — | exploratory (tester robot) |
| Worktree outlives its ticket, or the ticket its worktree (gizmo-01, 07, 08, 09, 15, 16) | `space/repo`, `space/kanban` | Activate answered success and opened nothing after the worktree folder was deleted; a folder left after its branch was deleted blocked activate for good. Delete and archive left the worktree and branch, and delete could stop halfway. | `Worktrees` trusted git's list or the folder alone and never compared the two; delete and archive did not include the worktree. | `stale-state`, `false-success` | — | — | — | exploratory (tester robot) |
| Close does its steps in the wrong order (gizmo-14, 17) | `space/kanban` | A close whose merge conflicted had already removed the worktree and written the handoff; a close with merge committed and pushed the main clone's uncommitted edits. | `Ticket.close` removed and published before the merge was known to succeed, and `save_work` committed whatever checkout it stood in. | `data-loss` | — | — | — | exploratory (tester robot) |
| Guidance argument matching (widget-01, 02, 03) | `harness/guidance`, `harness/guidance_actions`, `cdd_guidance/actions` | A misspelled slug ran as plain text with no rules, a valid mapping was refused with a message that contradicted itself, and validate's `rule` argument could not be named through the cdd server. | Any string that matched no slug was treated as prose; the published schema for `rule` did not accept a rule's name. | `unchecked-input`, `false-success` | all | all | — | exploratory (tester robot) |
| Render saves over the wrong file (widget-04, 05, 06, 07, 09) | `cdd_guidance/actions` | Rendering any markdown file of the folder replaced the story map's drawing, a drawing rendered back overwrote `story-map.md` with the template's title, and a path outside the session's root was read and written. | `RenderedFile.save` named its output for the fidelity, not for the path given, and paths were not held to the session's root. | `data-loss`, `unchecked-input` | Stories | Discovery | drawio, whiteboard, markdown | exploratory (tester robot) |
| Calls that answer success and do less (widget-10, 11, 12; rivet-08) | `cdd_guidance/actions`, `space/session`, `scripts` | Validate with `graph: true` and no paths said no graph was checked, document ignored its paths, and a spec file that ran no examples counted as passed. Output roots accepted a file, `C:/Windows` or an empty path. | Empty or unusable input fell through to a quiet default answer instead of a refusal. | `false-success`, `unchecked-input` | all | all | — | exploratory (tester robot) |
| Record of test runs describes the wrong run (rivet-01 to 05, 09, 10) | `harness/diagnostics` | A tier's result was recorded under a commit it did not test, a run waited for ever on a process id another program now held, and a hand run on another checkout showed as main's result. A claim file left behind made runs wait without a word. | The record kept a commit, a process id and a claim with nothing that checked they still described a live run on that checkout. | `stale-state`, `concurrency` | — | — | json | exploratory (tester robot) |
| Files app on a file that is gone, odd or huge (pixel-01, 02, 03, 04) | `harness/files_app`, `space/session`, `space/repo` | A deleted file opened as an empty editor, a file with a non-ASCII name was never listed, a four megabyte file crashed the tab, and a missing project folder was reported as the cdd server not connected. | `FileManager.read` returned empty for a missing file, git's quoted names were not unquoted, and the editor loaded any size. | `raw-error`, `display`, `stale-state` | — | — | — | exploratory (tester robot) |

## Wave 2 — Round 2: defects reproduced by another robot, and the areas round 1 missed

Round 2 reproduced the round 1 defects from their reports alone; the themes below are what it added.

| Defect theme | Module(s) | Description | Root cause | Classification | Practice | Stage | Format | Caught by |
|---|---|---|---|---|---|---|---|---|
| A trip through another format loses prose (widget-08, 19, 20) | `cdd_guidance/practices` (Stories, Clean Engineering, DDD adapters) | A class model through a drawing lost descriptions, notes and calls; scenarios through code lost an outline's table, term links and prose; the bounded-context map and domain model lost integrations and invariants. | Each adapter rendered only what its format can hold, and the render saved the smaller result over the fuller markdown. | `lossy-format-trip`, `data-loss` | Stories, Clean Engineering, DDD | Discovery, Specification | drawio, whiteboard, python, typescript | exploratory (tester robot) |
| Graph leaves out what it cannot place (widget-18, 21) | `cdd_guidance/practices`, `harness/graph` | A Python file that stopped parsing dropped out of the graph, and scenarios of a story not on the map added nothing; validate then said everything passed. | A file that gave the graph no node was skipped without a violation. | `false-success` | Stories, Clean Engineering | Specification, Implementation | python, markdown | exploratory (tester robot) |
| Board and graph view on one bad file (pixel-07, 08) | `space/kanban`, `space/session` | One ticket's unreadable `session.json` blanked the whole board, and selecting a graph node whose file had moved left another node's file on show. | `Board.show` failed whole on one unreadable session; `NodeSpans.collect` kept the last file when the node's file was missing. | `raw-error`, `stale-state`, `display` | — | — | json | exploratory (tester robot) |
| Browser tests older than the page (pixel-09, 10) | `story_tests` | One test expected no whiteboard entry in another project's file bar, and one found two line texts in a changed line. Both failed before this session. | The tests and one scenario were not brought up to date when the page changed; one locator matches two elements by timing. | `rule-template-mismatch` | Stories | Implementation | typescript | exploratory (tester robot) |

## Wave 3 — Round 3, first pass: every fidelity of every practice in every format, on the Bookshop

| Defect theme | Module(s) | Description | Root cause | Classification | Practice | Stage | Format | Caught by |
|---|---|---|---|---|---|---|---|---|
| Thin slice has no format of its own (r3-sparky-01, widget-06) | `cdd_guidance/practices/stories` | Generate told the agent to save `thin-slice.md` and `thin-slice.drawio`, but the thin slice could not be chosen or drawn, and rendering it replaced the story map's drawing. | The fidelity declared no thin-slice file and had no template for it. | `undeclared-output`, `data-loss` | Stories | Discovery | drawio, markdown | exploratory (tester robot) |
| Story map back from a drawing (r3-sparky-02) | `cdd_guidance/practices/stories` | A story map rendered to drawio or whiteboard and back lost the descriptions under its epics, its story links and its scope. | The drawing adapters read back only names and nesting, and the result replaced the markdown. | `lossy-format-trip`, `data-loss` | Stories | Discovery | drawio, whiteboard | exploratory (tester robot) |
| Stories graph reading (r3-sparky-03, 05, 08, 09, 10) | `cdd_guidance/practices/stories`, `harness/graph` | Every story's Background was one node with no steps, a linked domain term was a fact on the step with no edge to the DDD class, and a Python step invoked the TypeScript operations of the same name. Story tests loaded with the map lost their invokes edges. | The reading matched operations by name alone and built a story test's place from its file, not from the map. | `name-matching` | Stories | Specification, Implementation | markdown, python, typescript | exploratory (tester robot) |
| Scenarios after the template fail validate (r3-sparky-04) | `cdd_guidance/practices/stories` | Markdown scenarios written exactly as the template shows failed with 12 graph errors, one for every Then. | A rule asked every Then to observe an Example, which the template does not write. | `rule-template-mismatch` | Stories | Specification | markdown | exploratory (tester robot) |
| Scenarios rendered to code (r3-sparky-06, 07, 11) | `cdd_guidance/practices/stories` | An outline's examples table rendered to Python or TypeScript did not parse, the render was one test named for no story, and generate at acceptance tests handed over Clean Engineering's Python class template. | The code adapter had no rendering of an outline and no per-story file; the fidelity had no acceptance-test template per language. | `lossy-format-trip`, `undeclared-output` | Stories | Specification, Implementation | python, typescript | exploratory (tester robot) |
| DDD model missing from the graph (r3-bolt-01, 05) | `cdd_guidance/practices/ddd`, `harness/graph` | The graph held none of the bounded contexts, integrations, events or cross-aggregate dependencies, and with code in place a context mapping linked to no aggregate. | The DDD reading read only classes, and matched an aggregate by its lower-case name. | `name-matching`, `false-success` | DDD | Discovery, Specification | markdown, python | exploratory (tester robot) |
| Domain model after the template fails validate (r3-bolt-02) | `cdd_guidance/practices/ddd` | A domain model written after the template failed with nine `conforms-to-schema` errors. | The schema and the template named the sections differently. | `rule-template-mismatch` | DDD | Specification | markdown | exploratory (tester robot) |
| Domain model drawing (r3-bolt-03, 04) | `cdd_guidance/practices/ddd` | The drawing showed an arrow for each integration and call but reading it back dropped them, and the drawio showed twelve loose class cards with no context or aggregate container. | The drawio adapter wrote arrows it did not read and drew no container shapes. | `lossy-format-trip`, `display` | DDD | Specification | drawio, whiteboard | exploratory (tester robot) |
| Model rendered to code (r3-bolt-06, 07; r3-widget-07) | `cdd_guidance/practices/ddd`, `clean_engineering` | The model rendered to Python or TypeScript was one text for every aggregate, saved nowhere, and a render to TypeScript kept Python's type spellings such as `list[CartLine]`. | A code render answered content instead of saving at the declared paths, and types were copied, not translated. | `undeclared-output`, `lossy-format-trip` | DDD, Clean Engineering | Specification, Implementation | python, typescript | exploratory (tester robot) |
| IA render empties the other file (r3-gizmo-01) | `cdd_guidance/practices/ux` | Rendering the IA drawing to markdown emptied `ux-context.md`, and rendering the context to drawio emptied the drawing. | Both formats were saved from a model read only from the format being rendered. | `data-loss`, `lossy-format-trip` | UX | Discovery | drawio, markdown | exploratory (tester robot) |
| UX drawings drop what they show (r3-gizmo-02, 04) | `cdd_guidance/practices/ux` | The IA drawing showed each screen's stories and domain terms and reading it dropped them; a mockup through its drawing lost all 12 controls, states and interactions. | The drawio adapter drew labels it had no reading for. | `lossy-format-trip` | UX | Discovery, Specification | drawio | exploratory (tester robot) |
| UX formats that cannot be rendered (r3-gizmo-03, 05) | `cdd_guidance/practices/ux` | A mockup rendered to `claude_design` answered `{}`, and neither format front-end code offered could be rendered to or from. | The formats were offered with no adapter behind them. | `undeclared-output`, `false-success` | UX | Specification, Implementation | claude_design, typescript, javascript | exploratory (tester robot) |
| UX is not in the graph (r3-gizmo-06) | `cdd_guidance/practices/ux` | No UX file in any format added a node or an edge to the knowledge graph. | UX had no graph reading. | `undeclared-output` | UX | all | all | exploratory (tester robot) |
| Modules drawing and whiteboard (r3-widget-01, 02, 03) | `cdd_guidance/practices/clean_engineering` | The modules drawing was saved in the first module's own `.context`, a module card lost its language and Constraint section through a drawing, and the whiteboard read back added a module `src` nobody wrote. | The save place came from the first path, and the adapters read folders as modules. | `lossy-format-trip`, `data-loss` | Clean Engineering | Discovery | drawio, whiteboard | exploratory (tester robot) |
| Class model in markdown (r3-widget-04, 05, 06, 08) | `cdd_guidance/practices/clean_engineering` | After one class model was rendered to markdown, every later model took the first one's class names; a markdown model gave the graph no class and validate said it passed. A model through Python lost relationship kinds and notes. | The markdown adapter kept state between renders, and markdown models had no graph reading. | `data-loss`, `false-success`, `lossy-format-trip` | Clean Engineering | Specification | markdown, python | exploratory (tester robot) |
| Code graph joined by name (r3-widget-09, 10) | `cdd_guidance/practices/clean_engineering`, `harness/graph` | A call was joined to every operation of that name, so `super().__init__` became an edge to every constructor; Python code gave no property node and no inheritance or composition edge. | Calls were resolved by operation name alone; the reading ignored properties and base classes. | `name-matching` | Clean Engineering | Implementation | python, typescript | exploratory (tester robot) |
| Java offered and never read (r3-rivet-01) | `cdd_guidance/practices/bdd` | BDD behavior and development offered Java and generate said to save it, but render refused Java and nothing read it. | A format listed with no adapter. | `undeclared-output` | BDD | Discovery, Implementation | java | exploratory (tester robot) |
| Validate passes a file it read nothing from (r3-rivet-02) | `cdd_guidance/actions`, `cdd_guidance/practices/bdd` | Validate on a BDD sketch or tree markdown read no node and said all scanned graph rules passed. | Validate did not report a path that gave the graph no node. | `false-success` | BDD | Discovery | sketch, markdown | exploratory (tester robot) |
| Spec trips between formats (r3-rivet-03 to 07) | `cdd_guidance/practices/bdd` | An observation moved below its nested state, a sketch was written as the plain tree, call-graph comments were not read back, and Python to TypeScript and back left every body commented out, wrapped again on each trip. | The adapters kept one ordered list of children per state and treated bodies as text to comment out, not to translate or keep. | `lossy-format-trip`, `data-loss` | BDD | all | sketch, markdown, python, typescript | exploratory (tester robot) |
| BDD realization and graph links (r3-rivet-08, 09, 10) | `cdd_guidance/practices/bdd`, `harness/graph` | The realization steps named `.context/graph.json` while `save_json` wrote elsewhere, an observation reading a property two classes name got no edge, and the shared-describe rule saw only double-quoted Python. | Guidance text and the tool disagreed on a path; links were by name; the rule's pattern matched one quoting style. | `rule-template-mismatch`, `name-matching` | BDD | Specification, Implementation | python, typescript | exploratory (tester robot) |

## Wave 4 — Round 3, second pass: the five practices combined, their graph and their display

| Defect theme | Module(s) | Description | Root cause | Classification | Practice | Stage | Format | Caught by |
|---|---|---|---|---|---|---|---|---|
| No edge crosses a practice (r3-cog-01, 05) | `harness/graph`, every practice's reading | One class was up to eight unjoined nodes across DDD, Clean Engineering, languages and folders, and a BDD observation linked to a same-named operation of another class; 15 of 31 BDD links and 51 of 57 story-test links were wrong. | Each practice read its own files into its own nodes, and the only join was a shared name. | `name-matching` | all | all | all | exploratory (tester robot) |
| Refresh and whole loads change the graph (r3-cog-02, 03, 04) | `harness/graph`, `cdd_guidance/practices/stories` | Refreshing unchanged Stories files detached code story tests from their stories and doubled or dropped scenarios; a whole load left out story tests in code, and a story test whose story was off the map raised nothing. | Refresh rebuilt nodes file by file without the map beside them, and the roots declared no code story tests. | `stale-state`, `false-success`, `undeclared-output` | Stories, DDD | Implementation | python, typescript | exploratory (tester robot) |
| Rendered markdown view (r3-pixel-01, 02, 07, 09) | `harness/files_app` | The rendered view dropped every class stereotype and generic type, showed front matter as the page's biggest heading, lost a BDD realization's indented tree, and showed underline marks as plus signs. | The new rendered view passed markdown to an HTML renderer that read angle brackets as tags and knew none of the practices' notations. | `display`, `regression` | all | all | markdown | exploratory (tester robot) |
| Links and callouts (r3-pixel-03, 04, 05) | `harness/files_app`, `space/session` | A link in the rendered view did nothing, the source view showed 14 of 28 link callouts, and story tests in code showed none. | Callouts were made only for links to a heading that exists, only in markdown, and only in the source view. | `display` | all | all | markdown, python, typescript | exploratory (tester robot) |
| Files no fidelity owns (r3-pixel-06, r3-lens-02) | `cdd_guidance/practices`, `space/session` | Fifteen of 102 practice files were in no list with every stage, practice and format on: story tests directly under an epic, each context's `bounded-context.md`, JSON maps and front-end views. | The fidelities' file declarations did not cover those paths. | `undeclared-output` | Stories, DDD, UX | all | markdown, json, typescript | exploratory (tester robot) |
| Graph view selection fails or marks the wrong lines (r3-lens-01, 03, 04, 07) | `space/session`, `harness/files_app` | Selecting a package, module or aggregate failed with a 500, a step holding a quoted phrase was placed at line 1, the second scenario marked the first, and a file changed on disk kept its old lines. | Folder nodes have no file (broken by the pixel-08 fix); markdown lines were found by searching for text; ranges were cached per file. | `regression`, `display`, `stale-state` | Stories, Clean Engineering, DDD | all | markdown, python | exploratory (tester robot) |
| Graph view filters (r3-lens-05, 06) | `space/session` | A practice turned off with no stage selected narrowed neither the list nor the graph view, and with every practice off the view failed with `PracticesNotRegistered`. | No selection and an empty selection were read as the same thing. | `raw-error`, `display` | all | all | — | exploratory (tester robot) |
| Graph tree entries and relationship members (r3-lens-08, 09) | `space/session`, `harness/files_app` | Selecting a node under a relationship group opened only the file that holds the relationship, and packages and same-named Python and TypeScript classes could not be told apart in the tree. | A member carried its holder's source; a tree label used only the last part of a name. | `display` | Clean Engineering, DDD | Implementation | python, typescript | exploratory (tester robot) |

## Wave 5 — Found while fixing: the fix waves' own tier runs and the person's use of the board

| Defect theme | Module(s) | Description | Root cause | Classification | Practice | Stage | Format | Caught by |
|---|---|---|---|---|---|---|---|---|
| Linking calls by import dropped real edges | `harness/graph`, Stories and BDD readings | The fix for name matching removed the invokes edges of this repository's own story tests and of operations whose parameter is a class the file does not import. The unit tier caught seven examples. | The first fix followed imports only; a receiver can also be typed by the class that built it or by an annotation. | `regression`, `name-matching` | Stories, BDD | Implementation | python | unit tier (BDD specs and story tests, domain tier) |
| Changed declarations and saved renders broke their neighbours | `space/session`, `harness/diagnostics`, `cdd_guidance/actions` | New file declarations moved a fidelity's proposed root up one folder, and saving code renders turned the install health probe red with `RenderHasNoDeclaredPlace`. The health report's new desktop walk question failed a heavy spec. | Specs and probes held the old shapes of answers that the fixes changed on purpose. | `regression` | all | all | — | unit tier (specs), heavy tier (install health probe, server health) |
| A render removed a person's note from a drawing | `cdd_guidance/actions/render` | A drawing that held only a person's note lost it when the story map was rendered onto it. Found while bringing two render examples inside the unit budget. | The render treated every cell it did not draw as its own stale output when no drawn cell remained to compare with. | `data-loss`, `lossy-format-trip` | Stories | Discovery | drawio | unit tier (render BDD spec, while restructuring it) |
| Three defects in every language | `cdd_guidance/practices/stories` | Writing the story test checks once on the model's graph, then running them for Python, TypeScript, JavaScript and markdown, found three defects present in all four. | Each language's adapter had been tested by its own examples, so a shared fault was never compared across them. | `lossy-format-trip` | Stories | Implementation | python, typescript, javascript, markdown | unit tier (shared behaviour story tests, domain tier) |
| False findings in the validation report | `cdd_guidance/practices/stories`, `space/kanban` | The report listed an epic's seven children against a 2 to 6 band the rule no longer used, and marked four behaviours whose names end in or hold "once" as one-time tasks. | The first was a report saved before the band changed and not marked out of date; the second was a scanner judging a name pattern where the rule needs judgment, now removed and judged. | `rule-template-mismatch`, `stale-state` | Stories | Discovery | markdown | exploratory, by the person on the board's report |
| Business rules decided on the page | `harness/files_app/app`, `space/kanban/app` | Which callouts show was worked out in the browser, and the Fix and False prompts are still built in TypeScript. The person's rule is that every application gets its logic from Python. | The page was written before the rule was stated; callout filtering has moved, the prompts and several file-list rules have not. | `rule-template-mismatch` | — | — | typescript | the person's review; no test |
| Graph view browser test fails only inside the tier | `story_tests` | `explore-graph-in-files-app.story.ui_e2e_spec.py` has failed in three e2e tier runs and passed its 13 examples each time it was run alone. | Not found. | `concurrency` (suspected) | Stories | Implementation | python | e2e tier (browser story test) |
| The chat bar cannot be walked from inside the Claude app | `cdd_guidance/desktop_walk` | The desktop walk asks computer control for the Claude app's own window, which is refused for good, so none of the six desktop story tests can run. | The walk was built without a real run of its first step; the app never grants control of itself. | `false-success` | Stories | Implementation | markdown | exploratory (the first real run of the walk) |

## What the themes say together

- **Rounds 1 and 2** found faults at the edges of the tools: two callers, unchecked names and paths, unreadable files, records that outlive their subject. `unchecked-input`, `concurrency`, `stale-state` and `false-success` carry 15 of the 19 themes.
- **Round 3** found faults in the practices themselves: `lossy-format-trip`, `name-matching`, `undeclared-output` and `rule-template-mismatch` carry 22 of the 28 themes, and three root causes repeat across all five practices: a format that holds less than markdown is saved over it, the graph joins by name, and a format or file is offered with nothing that reads it.
- **The fix waves** added `regression`: six of the eight themes are a fix, a changed answer or a newly built feature that nobody had run against its neighbours.
