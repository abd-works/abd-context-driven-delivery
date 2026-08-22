# context_tools/actions — peer action kits

## Purpose
Lifecycle and companion kits always used in the BaseContextTool frame. Deployed as
**skills and** Cursor commands / VS Code prompts. Kit-owned actions (`/iterate`,
`/sketch`, `/grill`, `/partition`, `/repair`) run their toolset once with
`arguments.tools` listing the in-scope context tool(s). Core lifecycle
(`/generate`, `/validate`, `/document`, `/satisfy`) is **host-owned** — each
named context tool runs `action: generate` (etc.) in order.

## Membership
Host-action kits: `sketch`, `iterate`, `grill_context`, `partition`,
`improvement`, `eval` (`eval.session:EvalSession`; agentic Repair deferred),
`workspace`
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
| `/repair` | `improvement.improvement:Improvement` | `repair(tools, asset, violation)` |

`/generate` … `/satisfy` — host-owned (`action: generate` on each context tool); no HostLifecycle kit.

Inner corpus/session actions (`iterate_session`, `partition_corpus`, …) stay on the kit for in-method composition.
