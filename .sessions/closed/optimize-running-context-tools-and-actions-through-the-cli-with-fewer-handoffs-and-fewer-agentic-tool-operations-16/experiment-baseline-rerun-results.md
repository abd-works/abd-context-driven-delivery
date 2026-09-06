# baseline rerun results

- branch: experiment/baseline
- options: none
- clock: clean (tools.ps1 + Generate kit; no session=; no OneDrive miss; no host action: generate)
- pair_a_story_map_generate:
  - start: 2026-08-27T13:45:05
  - end: 2026-08-27T13:46:28
  - elapsed: 01:23
  - artifact: sandbox/courier/.context/story-map.md
- pair_b_model_generate:
  - start: 2026-08-27T13:46:58
  - end: 2026-08-27T13:47:33
  - elapsed: 00:35
  - artifact: sandbox/courier/.context/clean-engineering-model.md
- notes:
  - First hop each pair: `.\tools.ps1 manifest generate.generate:Generate` then `.\tools.ps1 run _req.yaml` with Generate kit, host in `arguments.tools`, `path: sandbox/courier`, `session: null`.
  - Generate returned `tools: []` (Pair A) / drawio `create_diagram`/`scan`/`repair` (Pair B, skipped — format was markdown). Extra hops: Stories `action: guidance` then write story-map; CE `action: guidance` then write model. Did not call `open` / `session=` / generic `scanners.scan:Scan`.
  - Pair A `format: markdown`. Pair B copied catalog with `format: markdown` so the artifact is `clean-engineering-model.md` (catalog `format: null` would default to python).
