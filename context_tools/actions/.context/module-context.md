# context_tools/actions — peer action kits

## Purpose
Lifecycle and companion kits always used in the BaseContextTool frame. Deployed as
**skills and** Cursor commands / VS Code prompts. Kit-owned actions run their
toolset once with `arguments.tools` listing the in-scope context tool(s).

## Membership
Host-action kits: `generate`, `validate`, `document`, `satisfy`, `render`,
`sketch`, `iterate`, `grill_context`, `partition`, `improvement`
Companions that left this tree: `echo` and `handoff` live under `utilities/`;
`workflow` is still listed here until it moves.

Host-action skill/command names match the operation (`grill`, not `grill-context`).

`primitives/actions` is the Actions framework (`action.py`, `@agent_instructions`),
not a place for these kits. First-order kits subclass `LifecycleAction`: open the
workspace if it is not already open; the turn and decision records hang off the
work session; finish that session turn at the end.

Non-action tooling stays under `utilities/` (`scanners`, `diagnose`, …).

## Kit-owned actions

| Slash command | Kit | Outer action |
| --- | --- | --- |
| `/generate` | `generate.generate:Generate` | `generate(tools)` |
| `/validate` | `validate.validate:Validate` | `validate(tools)` |
| `/createRule` | `validate.validate:CreateRule` | `createRule(tools, failed, wanted)` |
| `/document` | `document.document:Document` | `document(tools, paths)` |
| `/satisfy` | `satisfy.satisfy:Satisfy` | `satisfy(tools)` |
| `/render` | `render.render:Render` | `render(tools, format, content)` |
| `/iterate` | `iterate.iterate:Iterate` | `iterate(tools)` |
| `/sketch` | `sketch.sketch:Sketch` | `sketch(tools)` |
| `/grill` | `grill_context.grill_context:GrillContext` | `grill(tools)` |
| `/partition` | `partition.partition:Partition` | `partition(tools, context, …)` |
| `/repair` | `improvement.improvement:Improvement` | `repair(tools, asset, violation)` |

Inner corpus/session actions (`iterate_session`, `partition_corpus`, `grill_with_context`, …) stay on the kit for in-method composition and keep `@agent_instructions` only — they are not slash files.

Outer actions carry `@prompt` (and `@prompt(name=…)` when the slash name is not the class slug: `/grill`, `/repair`, `/createRule`, `/backlog`, `/start-ticket`, `/finish-ticket`). Unmarked helpers do not get commands.
