# cdd_guidance/actions
*Actions* are the shared verbs every practice is worked with: you pass one or more *Guidance* — a practice at its current fidelity, such as `stories-story-map` or `clean-engineering-modules` — and the action runs once for each, so no practice reimplements opening the session, reading its rules, or saving its reports. Each action is a toolset built on *GuidanceAction* from `harness/guidance_actions`.

This module holds the core lifecycle verbs; their folders have no card of their own and roll up to this one:

- *Generate* writes each listed Guidance's artifact at its current fidelity, with that fidelity's rules and the shared rules of each pattern the session overlays (`## Pattern overlay: <pattern>`), then has the result validated (`generate.generate`).
- *Document* records what already exists for each listed Guidance without correcting it, so violations are flagged, not fixed (`document.document`).
- *Validate* checks artifacts against each listed Guidance's rules and the shared rules of each pattern the session overlays (`## Pattern overlay: <pattern>`, as Generate gives them), adds the graph rules' hits for graph-backed practices, and saves a report in the session's `validation-reports/` folder (`validate.validate`); *CheckedGraph* is the graph one call checks and the files it is built from: it holds the fidelity each listed practice is checked at, reads each one's checked format once, and keeps the graph it builds so its violations are read from that graph, not from the file written for the report; asked for the session's saved graph, it reads the file the session's graph saves in (`Graph.saved_file`). *ReportFiles* are the reports the call saves, and *ValidationReport* writes one from the listed guidance it holds: the rules each guidance checks (`checked_rules()`), and for a graph hit of a rule it does not check, that rule as the guidance has it (`every_rule()`). `Validate.create_rule` adds a named rule from a failed example and the behaviour wanted; it carries `@noDeploy`, so it is called from Python and is not an installed MCP operation or slash command.
- *Satisfy* gives the listed Guidance's rules, lists `validate` as the tool the agent calls before and after its fixes, and names the fixes step of the Generate it starts (`Generate.generate_fixes_from_validate`) (`satisfy.satisfy`). Expanding it checks nothing, so it saves no report and logs no validate line.
- *Render* converts content a practice already generated into another format, such as markdown into drawio (`render.render`). It only converts: it opens no session and commits nothing, and with `paths` it reads the files itself, once.

## How a recipe reaches its text

An action's instructions are its `@agent_instructions` recipe, which the MCP host expands from the call's arguments without running the recipe as Python. Only three shapes put text into the prompt:

- a string statement, or `instructions(text)` with a text the recipe computed;
- a recipe or tool named on another action the recipe starts, such as `instructions(self._generate().generate)` or `tools(self._validate().validate)`. The other action is made with `_inside`, so it already works on what this one lists, at the same fidelity, and it logs nothing: building a sketch's instructions runs the generate recipe they end with, and a generate line would tell the session board generate is done before anything is written. An action held as a tool (`as_tool()`) is listed by name instead of pasted in;
- a callback passed to `each` or `run`, which hands it the fidelity this action works at on each listed practice, and whose returned text the recipe reads.

A recipe called as an ordinary Python method, such as `grill.grill_with_context()` inside a callback, gives the prompt only its return value. `fidelity_text_spec.py` expands each action that writes or fixes an artifact this way and checks that the fidelity's instructions, template, rules, and tools arrive; it also answers each recipe the way an MCP client calls it, with only its required arguments, and checks that the session log holds only the action's own lines.

The other actions are separate modules with their own cards: `actions/diagnose`, `actions/grill_context`, `actions/improvement`, `actions/iterate`, `actions/partition`, and `actions/sketch`.

- **Purpose:** Give every practice the same generate, document, validate, satisfy, and render steps, so a practice owns only its words, rules, and formats.
- **Seam (terms):** Generate, Document, Validate, Satisfy, Render, `generate.generate`, `document.document`, `validate.validate`, `satisfy.satisfy`, `render.render`
- **Dependencies (one-way):** `harness/guidance_actions` (*GuidanceAction*, *GuidanceArg*, `load_document`), `harness/guidance` (*PracticeGuidance*, *Rule*, *PracticeCatalogue*), `harness/graph` (graph rule checks, and *SavedGraph*, the saved graph a report reads), `harness/markdown` (*Format*), `harness/agent_tools`, `harness/installation`, `harness/mcp`

## Constraint

Pass the practice into the action — `generate.generate(guidance=["clean-engineering-modules"])` — rather than putting a lifecycle verb on the practice class. Pass files by path; an MCP call never carries a document body. A relative path a call names is read from the project of the session the call works in (`path_named(path)`, and `document_named(content, paths)` for a document, on every *GuidanceAction*), never from the cdd server's own working folder. Name the files being edited in `paths` when validating, so the graph is built from just those files. An action's slash name is the operation's name (`/generate`, `/validate`), and helper instructions such as `generate_fixes_from_validate` are reached from an action's own instructions, not as slash commands.
