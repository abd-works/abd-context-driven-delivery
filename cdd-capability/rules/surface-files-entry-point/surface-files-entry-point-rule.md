---
rule: surface-files-entry-point
kind: shape
fidelity: [engineering]
artifact: *.md
scanner: surface-files-entry-point-scanner.py
---

# Rule: Surface Files Entry Point

Every capability folder must contain an agentic surface `{capability}.md` and an API surface `{capability}.py`, both named after the folder, alongside `.cdd-config.json`. The `.md` file must open with a one-sentence description — no filename heading.

## DO

- Name the agentic surface `{folder-name}.md` and open it with a one-sentence description
- Name the API surface `{folder-name}.py` and expose `CapabilityCli` with `execute(argv) -> int`
- Include `.cdd-config.json` to identify the folder as a capability

## DON'T

- Use `README.md`, `index.md`, or any name other than `{folder-name}.md` for the agentic surface
- Open `{capability}.md` with a heading that repeats the filename (e.g. `# my-capability`)
- Use `index.py`, `main.py`, or any name other than `{folder-name}.py` for the API surface
