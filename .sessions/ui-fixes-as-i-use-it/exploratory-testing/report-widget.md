# Report: Widget, charter C4 (diagrams, story explorer, scenario reader)

Sandbox: `scratchpad/et/diagrams/sandbox` (a `pml-web` copy of `test-area/pml-web`, and `shop`, the Stories bookshop fixture plus the Clean Engineering ordering model, with the layouts added: a sub-epic file holding two stories, markdown beside Python, markdown beside TypeScript, a scenario renamed in markdown only, a scenario name with accents and punctuation, and a repository block). `CDD_HOME` was the throwaway `et/diagrams/cdd-home`. Everything ran in-process through `Render().for_call(ToolCall({}, root))`, `Graph().load_files`, Stories graph rules (`SchemaRuleRun`) and the story canvas's explorer (`ClaudeDesignStoryMap` + `CanvasExplorer`). I started no server, published nothing and committed nothing outside the sandbox. Notes, one line per probe: `sandbox/notes.md`.

## What I tested

- Story map to drawio, pml-web and shop: links, anchors, overlaps, rendering twice.
- Domain or class model to drawio and whiteboard, pml-web (40 classes) and shop: arrows (duplicates, both directions, dangling, shared routes), overlaps, rendering twice; drawio back to markdown; markdown to Python and back (class language in the doc comment).
- Heading anchors: the Python `heading_anchor` compared with the Files app's `headingAnchorOf` on 9 awkward headings (non-ASCII, punctuation, emoji, tabs, double spaces). They agree.
- Scenario reader on every layout: the scenarios of each story, the file each comes from, step code bodies, and Stories rules on the merged result.
- Story explorer tree: pml-web's Choose Lines and shop. Checked the realizations for each When group, the file:line behind each open ⧉, duplicate rows, and the class cards with their language.

## Defects (in `defects/`)

| File | Severity | In short |
|---|---|---|
| widget-1-domain-model-roundtrip-moves-language-to-kept.md | wrong result | pml-web model drawn to drawio and straight back to markdown is rewritten: language, invariants, comments, interactions and repositories go under "Kept from this file", and the front matter is lost |
| widget-5-ce-render-reads-context-headings-as-classes.md | wrong result | clean-engineering-model reads pml-web's `## context / ### aggregate / #### Class` model as 6 classes named after the `##` headings, with no arrows; ddd-model draws the 40 classes and 53 arrows |
| widget-6-explorer-code-scenarios-line-0-wrong-file.md | wrong result | Explorer opens every scenario written in code at line 0; duplicate rows name the wrong file |
| widget-4-drawio-story-link-misses-sub-epic-and-shared-files.md | wrong result | A story's drawio link reaches its scenarios only when the file is named after the story; sub-epic and shared files link back to the map |
| widget-3-step-loses-code-body-when-counts-differ.md | wrong result | A markdown step silently loses its code body when the code has one more `.and` and the words differ by a link |
| widget-8-repository-block-merged-into-root-class.md | wrong result / question | A `**XRepository** «Repository»` block in the template layout is not drawn in drawio; in Python its methods land on the root class and its property is dropped |
| widget-2-question-renamed-scenario-shown-twice.md | question | A scenario renamed in markdown only is held twice and no rule reports it; a shared file plus a screen spec give a scenario twice |
| widget-7-explorer-class-card-shows-raw-markdown.md | cosmetic | Class card title and language show `**` and `*` literally |

## What held

- Story map drawio: links go to the story's own file, or else to a map heading whose anchor exists. No overlaps. Rendering twice gives byte-identical output.
- DDD model drawio and whiteboard: no duplicate, two-way or dangling arrows, and no overlapping cards. Rendering twice keeps the same cells.
- A template-layout CE model round-trips through drawio byte for byte, and its class language survives Python doc comments with paragraph breaks and bullets intact.
- The scenario reader handles a sub-epic file with two stories, markdown beside TypeScript with the same names (merged, code bodies attached), and non-ASCII or punctuated scenario names.
- In pml-web's explorer, every When group has its realization.

## Still at risk

- Projects in pml-web's own model layout (`#### Class`, repository blocks inside the root's section). The CE readers and writers only know the template layout (widget-1, 5, 8), and pml-web is the real user of these files.
- Code-written scenarios in the explorer and in links (widget-4, 6). The specs cover pml-web's markdown and leave code layouts out.
- Merging markdown and code: pairing steps by words then by position, and matching names exactly, both drop or duplicate silently, with no rule reporting it (widget-2, 3).
- Arrow trunks: in the DDD whiteboard, 3 groups of arrows leave the same side of a card with the same bend, so they share a segment. I did not report it because it may be intended, but nobody has checked it by eye.

## Not reached, and why

- Pressing links live in the draw.io viewer and Files server. It needs my own Files server, and the viewer sends links to it. I compared the anchor code instead and read `DrawioLink`: a renamed file gets a 404 and the chat is told.
- The full story canvas render with screens (needs a stack pattern's fixtures) and its screen-group realizations. Publishing a whiteboard or canvas was out of bounds.
- TypeScript and JavaScript class-model round trips (I only did Python). Validate through a session (`validate graph=true`): I ran the rules directly on the graph instead.
