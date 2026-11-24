# Validation reports of the release-1-2-fixes session

Start with the session's final report, [release-1-2-fixes-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\release-1-2-fixes-report.md). Its sections 5 and 6 read these reports: which rule would have caught each error of the refactor, and the findings and code measures before and after. The files here are kept unchanged as history.

## The Validate action's reports

Each run of the Validate action writes a report named for its guidance and the time it ran, `<practice>-<fidelity>-<yyyymmddThhmmss>.md`, with the same findings as `.json` beside it. A name ending `_2` is a second report written in the same second. The graph each run checked is kept in `../.context/checked-graphs/` under the same name, and every finding's history (found, fixed, judged) is in [violation-history.jsonl](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\violation-history.jsonl).

| Reports | What they checked |
|---|---|
| `clean-engineering-code-*` | The code fidelity of Clean Engineering. Two of them are the start and the end of the refactor: [clean-engineering-code-20261121T212842.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261121T212842.md), the whole codebase before the judges' fixes (388 graph findings; it writes its first 13 rules twice, so it lists 503), and [clean-engineering-code-20261123T205308.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261123T205308.md), after the refactor and the new checks (2,733 violations and 2,972 candidates, 1,831 of the violations saying the measuring tool lizard is not installed). The earlier ones, from 2026-11-18 to 2026-11-21, checked the files a fix wave changed. |
| `clean-engineering-model-*`, `clean-engineering-modules-*` | The class model and the module cards, 2026-11-19. |
| `stories-story-map-*`, `stories-scenarios-*`, `stories-acceptance-tests-*` | The story map, the scenario files and the story tests, as the fix waves of exploratory testing changed them. |
| `ux-ia-*` | The UX information architecture, 2026-11-18. |

Reports newer than 2026-11-23 may appear here while robots are still working; the final report reads only those named above.

## The judges and the measures

| File | What it is |
|---|---|
| `judgment-guidance-graph.md`, `judgment-harness-apps-tools.md`, `judgment-harness-lower.md`, `judgment-kanban-repo.md`, `judgment-practices-ce-ddd-bdd.md`, `judgment-space-session.md`, `judgment-stories-ux-actions-patterns.md` | 2026-11-21. Seven judges' reading of every production file, one area each, against the Clean Engineering rules and the refactor guardrails: findings, fixes that change no design, proposed design changes, and graph findings judged noise. The proposals were merged into [design-proposals.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\design-proposals.md). |
| [code-measures-before-and-after-judge-fixes.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\code-measures-before-and-after-judge-fixes.md) | 2026-11-22. The code measured with lizard before the judge-led reshape (`33b3839e3`) and after it (`3c77725bc`): functions and classes past each limit, import loops and coupling. |
| [measure_checkout.py](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\measure_checkout.py) | The script that made that report: it validates one checkout's production code and counts each limit rule's violations. |
