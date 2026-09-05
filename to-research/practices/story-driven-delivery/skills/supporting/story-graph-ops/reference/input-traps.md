# Input traps — story-graph-ops

Pre-flight only — not grill questions.

- **Hand-rolled JSON** — Did you write JSON without running **`story_graph_cli.py read`** afterward?
- **Wrong authority** — Are you using another codebase's loaders as the *only* proof the file is valid for **story-graph-ops**?
- **PYTHONPATH skipped** — Can `import story_map` succeed from this skill's `scripts/`?
- **Concurrent write** — Will parallel runs touch the same slice without `--expect-sha` and the advisory lock?
- **Parser fallback** — When a markdown parser exits code 2, did you create a `_<variant>` script instead of hand-patching JSON?
