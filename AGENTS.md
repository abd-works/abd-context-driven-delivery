When editing file:
- all paths need to be absolute from to root so as to minimize impact of changing paths
- all skills should be refennced by name not path so they are dplotment location independant

## Cursor Cloud specific instructions

This is a pure-Python (3.12) CDD tooling repo with **no dependency manifest**. The only
third-party dev dependencies are `pytest`, `mamba`, and `expects`; the startup update
script installs them (`pip install --user`). No build step, no services, no network needed.

Run everything from the repo root (`/workspace`). Commands are invoked as
`python3 -m ...` / `python3 <script>` so the repo root is on `sys.path` automatically —
**no `PYTHONPATH` is required**.

Capabilities (each has a `.md` agentic surface + `.py` API surface):
- `/workspace/cdd-capability` — define/deploy CDD capabilities. CLI: `python3 /workspace/cdd-capability/__main__.py {list,deploy,clean,inject}`.
- `/workspace/enforce` — rules + scanners that validate artifacts. Scanner CLI: `python3 -m enforce.scanners validate <file>`.
- `/workspace/stories` — the largest capability. Skill workflow is in `/workspace/stories/SKILL.md`; the deterministic code path is `python3 /workspace/stories/cli/main.py` (see `/workspace/stories/cli/README.md`); the assembler is `/workspace/stories/src/skill/assembly/assemble_components.py`; validation is `python3 /workspace/stories/src/skill/run_scanners.py --workspace <ws> --rules-root /workspace/stories/rules`.

Testing (two runners, non-obvious discovery gotchas):
- **mamba** BDD specs (files ending `_spec.py`): `python3 -m mamba.cli /workspace/stories/src/stories`. Mamba's directory scan only finds `*_spec.py`; the specs under `/workspace/stories/tests/domain/` use a `spec_` **prefix**, so pass them explicitly, e.g. `python3 -m mamba.cli /workspace/stories/tests/domain/spec_fidelity.py`.
- **pytest**: the enforce test files end in `-test.py` (hyphen, not `_test.py`/`test_`), so pytest will **not** auto-collect them by directory — pass the file path explicitly, e.g. `python3 -m pytest /workspace/enforce/scanners/validate-artifact-scanner-test.py`.

Known caveats (pre-existing, not environment issues):
- `python3 -m mamba.cli /workspace/stories/src/stories` has 3 pre-existing failures in `markdown_story_map_spec.py` (scenario-parsing assertions). Everything else passes (306/309).
- The `stories` code CLI `py`/code backends fail because `tree.py` resolves templates at `/workspace/templates/py` instead of `/workspace/stories/templates/py`. The `md` backend works; use it for smoke tests.
- Agent-evaluation tests (`/workspace/enforce/rules/validate-artifact-rules-test.py`, `/workspace/agent_test`, and `/workspace/stories/src/skill/evals`) require the `cursor-agent` CLI + `CURSOR_API_KEY` (see `/workspace/stories/conf/.secrets`). They are skipped unless that external credential is provided.
