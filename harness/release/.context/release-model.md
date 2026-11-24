# harness/release

The CDD version and its release, never on red, and the slow test tiers run on a cadence whose results a release reads.

- **Purpose:** Say which CDD version a chat runs, set and release the next one, and keep the heavy and e2e tiers running on main so a release knows they passed.
- **Seam (terms):** CddVersion, Version, VersionStanding, VersionNotValid, ProjectVersion, CddRelease, ReleaseNotes, ReleaseOnRed, ReleaseAlreadyTagged, GitHubCli, TestCadence, TestTier, TestRun, TestRunRecord, TestRunRecordUnreadable, TestRunner, RunWorktree; the MCP operations `cdd-version.check`, `cdd-version.read`, `cdd-version.set_next` (`/version`), `cdd-version.release` (`/release`)
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/mcp, harness/process, harness/git, harness/e2e_review

## ProjectVersion

The version of a project, the one reader and writer of the `version` line of its `pyproject.toml`.

+ ProjectVersion(pyproject: Path)
------
+ version: Version
----
+ of(project: Path): ProjectVersion
+ read(): str
+ write(version: str): None

## TestRun

One run of a tier on one commit of one checkout: when it started, the process that runs it, how it ended, and the last lines it printed.

+ TestRun(tier: TestTier, commit: str, started_at: datetime, outcome: RunOutcome = RunOutcome.RUNNING, checkout: str = '', pid: int = 0, process_started: datetime | None = None, finished_at: datetime | None = None, summary: str = '', is_new_failure: bool = False)
------
+ tier: TestTier
+ commit: str
+ checkout: str
+ started_at: datetime
+ pid: int
+ process_started: datetime | None
+ is_live: bool
	// live only while the process it names runs: one with its id that started when the record says
+ name: str
+ state: str
+ run_id: str
+ started: str
+ summary: str
+ is_new_failure: bool
----
+ from_json(json_data: dict): TestRun
+ to_json(): dict
+ taken_by(process: RunningProcess): TestRun
	// the run keeps the process's id and when it started, which together name that one process
+ finished(exit_code: int, output: str, previous: TestRun | None, now: datetime): TestRun
+ is_due(now: datetime): bool
---<<names the process that runs it as>>--> RunningProcess

## TestRunRecord

The latest run of each tier on one checkout, and the finished run before it, kept with every other checkout's in `test-runs.json` in the cdd home. One process at a time looks at what is due: it claims the file `test-runs.claim` beside the record, and a claim left by a process that ended is taken over once it is stale.

+ TestRunRecord(folder: Path | str, checkout: Path | str | None = None)
------
+ folder: Path
+ path: Path
+ checkout: Path | None
+ runs: list[TestRun]
+ claim_wait: str
----
+ latest(tier: TestTier): TestRun | None
+ previous(tier: TestTier): TestRun | None
+ new_run(tier: TestTier, commit: str, started_at: datetime): TestRun
+ save(run: TestRun): None
	// the file is put in place whole, so a reader never meets half a record
+ claimed(): Iterator[bool]
+ log_path(tier: TestTier): Path
---<<keeps>>--> TestRun
---<<raises>>--> TestRunRecordUnreadable

## TestRunRecordUnreadable : Exception

The record's file holds something that is no record of test runs. It is left as it is, for a person to mend or remove.

+ TestRunRecordUnreadable(path: Path, held: object, reason: str)
------
+ path: Path
----

## RunWorktree

The folder a run's tier works in: a detached git worktree of the checkout, holding the files of the commit the run records, so a tier never tests a folder that goes on changing under it.

+ RunWorktree(record: TestRunRecord, run: TestRun)
------
+ folder: Path
----
+ made(): Iterator[Path]
	// the folder while the tier runs, removed after; one a killed run left is removed first
---<<runs git worktree through>>--> Git

## TestRunner

The boundary to `scripts/test.ps1` for one record's checkout: start a run in a background process that records its own result, or run one here and answer its exit code and output.

+ TestRunner(record: TestRunRecord)
------
----
+ start(run: TestRun): RunningProcess
	-> BackgroundStart.run
+ run(run: TestRun, env: dict[str, str] | None = None): tuple[int, str]
	-> RunWorktree.made
	-> StarterBoundJob.take_in
	// killing the runner ends its test.ps1 and the specs under it

## TestCadence

Runs heavy every hour and e2e every day on the main checkout its record is of. Nothing keeps time: `start_due` is called whenever the health report is read, and starts the overdue tier, one run at a time.

+ TestCadence(record: TestRunRecord, runner: TestRunner | None = None, git: Git | None = None, clock: Callable[[], datetime] = _utc_now, review: Callable[[Path, str], list[str]] | None = None, wait: Callable[[float], None] = time.sleep, say: Callable[[str], None] = _say)
------
+ << association >> record: TestRunRecord
+ checkout: Path | None
+ latest_runs: list[TestRun]
----
+ due(): list[TestTier]
+ start_due(): TestRun | None
	-> TestRunRecord.claimed
	-> TestRunner.start
+ run_now(tier: TestTier, recorded_start: datetime | None = None): TestRun
	// a run started while another is live, on any checkout, waits and says each time what it waits for
	-> TestRunner.run
	-> TestRunRecord.save
