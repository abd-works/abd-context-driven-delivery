# context_tools/actions — peer action kits

## Purpose
Lifecycle and companion kits always used in the BaseContextTool frame. Deployed as
**skills and** Cursor commands / VS Code prompts. Kit-owned actions (`/iterate`,
`/sketch`, `/grill`, `/partition`, `/generate`, `/validate`, `/document`,
`/satisfy`, `/repair`) run their toolset once with `arguments.tools` listing the
in-scope context tool(s).

## Membership
Host-action kits: `sketch`, `iterate`, `grill_context`, `partition`, `host_lifecycle`, `repair` (`eval.session:Repair`), `workspace`
Companions: `echo`, `handoff`

Host-action skill/command names match the BaseContextTool operation (`grill`, not
`grill-context`). Companions keep their own kit name (`echo`, `handoff`).

Non-action tooling stays under `utilities/` (`scanners`, `diagnose`, `agent_skills`, …).

## Kit-owned actions

| Slash command | Kit | Outer action |
| --- | --- | --- |
| `/iterate` | `iterate.iterate:Iterator` | `iterate(tools)` |
| `/sketch` | `sketch.sketch:Sketcher` | `sketch(tools)` |
| `/grill` | `grill_context.grill_context:GrillContext` | `grill(tools)` |
| `/partition` | `partition.partition:Partition` | `partition(tools, context, …)` |
| `/generate` … `/satisfy` | `host_lifecycle.host_lifecycle:HostLifecycle` | `generate(tools)`, etc. |
| `/repair` | `eval.session:Repair` | `repair(tools, asset, violation)` |

Inner corpus/session actions (`iterate_session`, `partition_corpus`, `repair_session`, …) stay on the kit for in-method composition.
