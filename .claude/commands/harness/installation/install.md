Install CDD into ``.cursor`` (or ``.claude`` with ``--ide Claude``) — skills, commands, rules, MCP, and hooks. ``replace`` wipes the previous install first.

Installer-only refresh (``/install`` and ``/clean`` without walking the catalog): ``python scripts/install.py --self`` from this repo — not MCP.

When install finishes, read ``.cursor/diagnostics.json`` (latest ``diagnose_install`` report) and paste the full summary: color, channel deltas, mcp host, hook server, hooks registered.

Run from the repository root with the Shell tool:

```text
python "C:\dev\abd-context-driven-delivery\scripts\install.py"
```
