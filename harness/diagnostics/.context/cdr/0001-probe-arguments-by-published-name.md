# Probe arguments and skips are kept by each operation's published MCP name

The diagnostics probes keep what they call each operation with, and which operations they leave alone, in tables keyed by the name the operation is published under on MCP: `render.render`, `partition.partition`, `repo.push_commit`, `improvement.repair`. They live in `probe_arguments.py`, `agent_tools_probe.py` (`_SKIP_INVOKE`, `_INVOKE_SKIP_PREFIXES`, `_HEAVY_INVOKE_PREFIXES`), and `guidance_probe.py` (`_LEFT_ALONE`). The agent tools probe also chooses the toolsets it covers by the module each toolset reference names, read from the install record in `diagnostics.json`.

Round 6 (R6-M2, and R6-M11 for the probe) asked for each operation to declare its own probe arguments, or that it is skipped, on its annotation, and for the probe to take toolset classes instead of references.

## Decision

Keep the tables in diagnostics, keyed by published name, and keep reading the install record's references.

- **A published name is a public contract, not a module.** Installed instructions, slash commands, and every chat call an operation by its MCP name, and this refactor keeps those names unchanged. A probe that knows `render.render` depends on what the install published, which is exactly what it checks; it imports nothing from `cdd_guidance`, `space`, or `tools`.
- **Probe data on the annotation would put the checker inside the checked module.** The module's constraint is that a module never imports its own checker. An annotation such as `@probe(paths=...)` would have every action, session, and repository operation carry diagnostic fixtures and a diagnostics concept, and a change to the probe would touch every module it probes.
- **The install record is read from a file.** `diagnostics.json` lists what the last install deployed as `module:Class` references. Turning those back into classes only to compare them with the classes the host loaded would import every toolset the record names, including ones the host skipped, which the probe must report rather than load.
- **Every skip is reported.** Each operation left alone shows as yellow with its reason, and the tool's description names every skipped operation and prefix; a spec (`agent_tools_diagnostics_spec.py`, "the agent tools diagnostics tool's description") fails when the description and the tables disagree.

## Consequences

Adding an operation that must not be called by a probe means adding its published name to the probe's table, with its reason. Renaming a published operation means renaming it here too, as every installed instruction that names it must change.
