# cdd_guidance/actions
*Actions* are the shared verbs every practice is worked with: you pass one or more *Guidance* — a practice at its current fidelity, such as `stories-story-map` or `clean-engineering-modules` — and the action runs once for each, so no practice reimplements opening the session, reading its rules, or saving its reports. Each action is a toolset built on *GuidanceAction* from `harness/guidance_actions`.

This module holds the core lifecycle verbs; their folders have no card of their own and roll up to this one:

- *Generate* writes each listed Guidance's artifact at its current fidelity, with that fidelity's rules, then has the result validated (`generate.generate`).
- *Document* records what already exists for each listed Guidance without correcting it, so violations are flagged, not fixed (`document.document`).
- *Validate* checks artifacts against each listed Guidance's rules, adds the graph rules' hits for graph-backed practices, and saves a report in the session's `validation-reports/` folder (`validate.validate`); *CheckedGraph* is the graph one call checks and the files it is built from, *ReportFiles* the reports it saves, and *PracticeRules* the shared and fidelity rules it checks. `Validate.create_rule` adds a named rule from a failed example and the behaviour wanted; it carries `@noDeploy`, so it is called from Python and is not an installed MCP operation or slash command.
- *Satisfy* validates, applies the fixes the report implies, and validates again (`satisfy.satisfy`).
- *Render* converts content a practice already generated into another format, such as markdown into drawio (`render.render`).

The other actions are separate modules with their own cards: `actions/diagnose`, `actions/grill_context`, `actions/improvement`, `actions/iterate`, `actions/partition`, and `actions/sketch`.

- **Purpose:** Give every practice the same generate, document, validate, satisfy, and render steps, so a practice owns only its words, rules, and formats.
- **Seam (terms):** Generate, Document, Validate, Satisfy, Render, `generate.generate`, `document.document`, `validate.validate`, `satisfy.satisfy`, `render.render`
- **Dependencies (one-way):** `harness/guidance_actions` (*GuidanceAction*, *GuidanceArg*, `load_document`), `harness/guidance` (*PracticeGuidance*, *Rule*, *PracticeCatalogue*), `harness/graph` (graph rule checks), `harness/agent_tools`, `harness/installation`, `harness/mcp`

## Constraint

Pass the practice into the action — `generate.generate(guidance=["clean-engineering-modules"])` — rather than putting a lifecycle verb on the practice class. Pass files by path; an MCP call never carries a document body. A relative path a call names is read from the project of the session the call works in (*PathsFromProject*, `actions/project_paths.py`), never from the cdd server's own working folder. Name the files being edited in `paths` when validating, so the graph is built from just those files. An action's slash name is the operation's name (`/generate`, `/validate`), and helper instructions such as `generate_fixes_from_validate` are reached from an action's own instructions, not as slash commands.
