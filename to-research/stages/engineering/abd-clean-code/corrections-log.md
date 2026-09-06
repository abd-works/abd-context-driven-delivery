# abd-clean-code — corrections log

## Entry 1 — JS scanners ImportError (JsCodeScanner vs agile_bots JSCodeScanner)

| Field | Content |
| --- | --- |
| **Context** | Slot 42 reviewer — `run_scanners.py --language javascript` crashed 17/17 on `ImportError: cannot import name 'JsCodeScanner'` because PYTHONPATH resolved `scanners.code.javascript` to `us_wires_demo/agile_bots` |
| **Status** | confirmed |
| **DO / DO NOT** | **DO** import the local base from `js_code_scanner` / `code_scanner` (skill `scanners/<lang>/` on PYTHONPATH). **DO** ship `run_scanner_main` + `__main__` on every scanner module. **DO NOT** import from `scanners.code.*` external packages. |
| **Example (wrong)** | `from scanners.code.javascript.js_code_scanner import JsCodeScanner` → ImportError on machines with agile_bots on PYTHONPATH |
| **Example (correct)** | `from js_code_scanner import JsCodeScanner` + `if __name__ == '__main__': run_scanner_main(...)` — scanners execute and report violations |
| **Likely source** | automation gap — scanners lacked CLI entrypoints; external PYTHONPATH shadowed local base class |

## Entry 2 — run_scanners false ALL CLEAN on import crash

| Field | Content |
| --- | --- |
| **Context** | ImportError exit code 1 with traceback treated as zero-violation pass |
| **Status** | confirmed |
| **DO / DO NOT** | **DO** treat stderr tracebacks / ImportError as scanner crash in `run_scanners.py`. **DO NOT** report ALL CLEAN when scanners fail to import. |
| **Example (wrong)** | Report status ALL CLEAN with 0 violations when every scanner traceback'd |
| **Example (correct)** | Overall status CRITICAL ISSUES + Scanner Failures section with traceback |
| **Likely source** | automation gap — exit code 1 conflated with rule violations |
