# Exploratory testing of release 1.2

Start with the session's final report, [release-1-2-fixes-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\release-1-2-fixes-report.md). It brings every file below into one account: each wave, its defects and their fix commits, the defects by module, the gaps in the tests, the refactor's errors, and the numbers before and after. The files here are kept unchanged as the history it was written from.

## In the order they were written

| File | What it is |
|---|---|
| [coverage-themes.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\coverage-themes.md) | 2026-11-19. What the scenarios and tiers covered before testing, and the eight kinds of behaviour the tiers reach only through fakes. The charters were written from it. |
| [charters.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\charters.md) | Each tester robot's charter, sandbox and test data, for rounds 1, 2 and 3. |
| [defects/](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\defects) | One file per defect or question, 156 in all: rounds 1 and 2 named by robot (`bolt-01`, `widget-12`), round 3 prefixed `r3-`. A file with `question` in its name waits on the person. Each file holds the steps, what was expected and seen, the tier that should have caught it, and its confirmation. |
| [closing-brief.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\closing-brief.md) | The brief every closing robot of rounds 1 and 2 worked from: a scenario, a test seen failing first, and the fix, for each confirmed defect. |
| [scribe-input.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\scribe-input.md) | What the closing robots added (stories, scenario files, classes), handed to the robot that brought the story map, module cards and class model up to date. |
| [final-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\final-report.md) | 2026-11-19. The report of rounds 1 and 2: defects by story and by class, the coverage added, the tier results, and the decisions left to the person. |
| [round-3-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\round-3-report.md) | 2026-11-19 to 2026-11-21. Round 3 (every fidelity of every practice in every format), the person's answers, and the five fix waves with their tier results. |
| [closing-brief-round-3.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\closing-brief-round-3.md) | The brief for round 3's fix waves: the person's answers as promised behaviour, and which robot owned which files. |
| [round-3-fix-shots/](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\round-3-fix-shots) | Screenshots of round 3's fixes seen working in a real browser, one folder per robot and wave. |
| [defect-themes-by-wave.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\defect-themes-by-wave.md) | 2026-11-21. Every defect grouped into themes for each wave, with module, root cause, tags, and the testing layer that should have caught it. |
| [defect-causes.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\defect-causes.md) | 2026-11-22. What produced the defective code, the shortcomings in the guidance behind it, and which measures of the code move with the defects. |
| [analysis/provenance.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\analysis\provenance.md) | Research for defect-causes.md: which guidance and tools were in use when each defective line was written, traced with `git blame`. |
| [analysis/guidance-gaps.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\analysis\guidance-gaps.md) | Research for defect-causes.md: what the guidance says, and does not say, about each kind of defect and each validation finding. |
| [analysis/code-metrics.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\analysis\code-metrics.md) | Research for defect-causes.md: which measures of the code would have flagged the defects. |
| [analysis/facts-by-node.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\analysis\facts-by-node.md) | The facts each node of the saved knowledge graph holds, by practice and node type, read for the code measures work. |
