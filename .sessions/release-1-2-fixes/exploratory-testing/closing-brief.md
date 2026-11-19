# Closing the gaps — brief for every robot

You close the gaps one module's defects showed. Several robots work in this checkout (`C:\dev\abd-cdd-release-1-2-fixes`, branch `release-1-2-fixes`) at the same time, each on its own module's files.

## What you produce, per confirmed defect

Work the defects in the order your card's prompt gives. A defect is confirmed when its file in `exploratory-testing/defects/` ends with a Confirmation section whose result is `confirmed`. Leave every file with `question` in its name alone: those wait for the person.

1. **Scenario** (`stories-scenarios`): a Given/When/Then scenario for the behaviour the defect breaks, in the scenario file of the story it belongs to under `story_tests/<epic>/<sub-epic>/`, or a new scenario file there when the story has none. Write the behaviour a source promises (a docstring, a module card, an existing scenario, a refusal the code already makes elsewhere). When no source says what should happen, do not invent it: write the defect's number in your report under "needs the person's decision" and move on.
2. **Test, written first, at the tier that owns the behaviour** (`stories-acceptance-tests`, the TDD supplement `cdd_guidance/practices/tdd/tdd.md`):
   - unit (`*_spec.py`, `*_story.test.py`) for a rule one object decides, with fakes, in milliseconds;
   - heavy (`*_heavy_spec.py`) for anything that needs real git, real files in two processes, a real cdd server, or the installer;
   - e2e (`*_e2e_spec.py`, `*.story.ui.spec.ts`) for what only shows on a page.
   Say which flow each change is in before writing it. Flow B (a heavy or e2e test already runs the boundary): failing test, see it fail for the right reason, then the code. Flow A (two real processes on one file, a boundary no test runs today): run it for real first — the tester's steps in the defect report are that run — capture it in a heavy spec, then add the unit specs.
3. **Fix** (`clean-engineering-code`): the smallest change that makes the test pass, on the object that owns the rule. Raise a named domain exception that carries the rejected value where the defect is a raw error or a silent wrong answer.

Before writing, call the Generate action for your slice: MCP tool `generate.generate` (load `mcp__cdd__generate_generate` with ToolSearch) with guidance `stories-scenarios`, then `stories-acceptance-tests`, then `clean-engineering-code`, and follow the rules it returns. After writing, call `validate.validate` with the same guidance and `paths` set to the files you wrote, and fix what it reports once. If an MCP call fails, stop that step and say so in your report; do not replace it with a shell call.

## Files you may change

Only the production and test files of the module your prompt names, the scenario files of that module's stories under `story_tests/`, and the module's own `.context/module-context.md` when a public name changes. You do not edit `.context/story-map.md`, `.context/model/*`, or any `*.drawio` / `*.whiteboard`: one robot brings those up to date after everyone. Report instead: each story or scenario you added (epic, sub-epic, story, file) and each class or public operation you added, renamed or removed.

## Guardrails

- Read `.sessions/_complete/integrate-practice-content-editor-apps/refactor-guardrails.md` first and answer its four questions on your own diff in your report. Do not bring back what was fixed before: parameters passed that the object could hold, lookups by name string, duplicated shapes, duplicated behaviour.
- Rename or reshape a public name in one pass: every caller and test updated, no alias left (`.claude/rules/coding.md`).
- Commit nothing and run no `git add`, `git stash`, `git checkout` or `git reset`: the lead commits after each robot reports.
- Run only your change's specs, in the foreground, the way `scripts/test.ps1` sets them up: `export CDD_HOME="$(mktemp -d)" PYTHONUTF8=1 PYTHONIOENCODING=utf-8; unset CLAUDE_CODE_SESSION_ID; python -m mamba.cli --format documentation <spec>` (`mamba.exe` is blocked on this machine). Never start a whole tier, and never run an install or a tier against the real checkout's own state or `~/.cdd`.
- Specs are Mamba: `describe` a domain subject, nest `with` / `that` (never `when`), one outcome per `it`.
- Write prose as `.claude/rules/writing-guidelines.md` says.

## Report

Your final answer, for the supervisor:
- per defect: fixed / test written and still failing (say why) / needs the person's decision / not reached;
- the spec files run, with the count that passed and failed, copied from the run;
- scenarios and stories added, and classes or operations added, renamed or removed;
- the guardrails' four answers;
- anything you changed outside your module, and why.
Mark your card done with `prompt-queue.done` on chat `0441e51a-b582-45e7-aefa-d95fcdc406e3` (find its id in your prompt).
