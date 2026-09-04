# scan

Run this action for any provided context tools, or on the context in general.

Action kit: ``/scan`` lists context tools; composed ``self.scanner`` is bound to the host.

scan

``tools`` names the context tool(s) whose scanner collection runs.
Slash ``/scan`` must pass them — a path-only scan has no rules.
Composed ``self.scanner.scan(paths)`` uses the host this kit was bound to.

``root`` defaults to ``cwd`` for ordinary project scans. Callers that
already know the narrow directory a scan belongs to (e.g. one
regression fixture folder) should pass it explicitly - a graph-wide
scanner (``StoryWorkspaceScanner``) loads everything under ``root``,
so an unscoped ``cwd`` makes it walk the whole repo.

``rule`` narrows the ``ok`` verdict to violations of that one rule
slug - a regression fixture built to exercise a single rule is not
a complete artifact and would otherwise trip every unrelated
scanner too.

If you took guidance from the context and not a tool, confirm the use of the context. AskQuestion constrained to the context tools: agent_bdd | bdd | cdd | clean_engineering | create_context_tool | ddd | stories | ux | use existing context only.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: scan.scan:Scan
tool: scan
```
python -m tools run -
