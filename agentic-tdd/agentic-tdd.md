---
extends: capability
overrides: [build, run, validate, generate]
---

Build and run cursor-agent tests using the Given / When / Then pattern.

## Build

Create a new agent test guided by the rules and template, then validate it.

read in full → `template/test_{feature}.py`
read `@rules` §Generate

Once written, run the structural validator:

```
python agentic-tdd/__main__.py build
```

## Run

Execute the agent test suite with pytest against a given path or the root of the capability being tested (all `test_*.py` files discovered recursively).

Agents under test operate inside an automated harness — they must:
- Act immediately; no clarifying questions
- Work only with what they are given (prompt, artifact, named files)
- Emit verdicts in the exact format the task specifies — verbatim, no preamble
- Be concise; output is parsed programmatically
- Assess and report only — do not fix violations

```
python agentic-tdd/__main__.py run [path] [-v]
```

- `path` — optional path to a single test file or directory; defaults to the root of the capability being tested (all `test_*.py` files discovered recursively).
- `-v` — verbose pytest output.

Agents under test must have `cursor-agent` on PATH and be authenticated (`cursor-agent login`).

## Validate

read `@rules` §Validate

## Generate

read `@rules` §Generate
