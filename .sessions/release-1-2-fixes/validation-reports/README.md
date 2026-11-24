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

Two runs came after the final report, on 2026-11-24 (UTC): [clean-engineering-code-20261124T010849.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261124T010849.md), the whole production code again and the latest whole-code state (2,616 violations, 1,808 of them saying lizard is not installed, and 2,920 candidates), and [clean-engineering-code-20261124T013014.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261124T013014.md), only the files of the review pass that followed it (323 violations, 101 candidates).

The second copy of the 2026-11-21 report, `clean-engineering-code-20261121T212842_2`, was byte for byte the same as the first and is removed; [violation-history.jsonl](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\violation-history.jsonl) still names its run.

## The judges, the measures and the rounds

The judges' reports, the design proposals, the code measures of the reshape, the measuring scripts, and every review round of the refactor before this release are in one folder, indexed in date order by [clean-engineering-review/README.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\README.md).
