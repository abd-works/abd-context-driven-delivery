---
generating-skill: abd-domain-specification
---

---

# Module: [stories/src/skill/evals]

Scope: Public-facing API of the eval runner — discovery, mode execution, result types, agent session management, and skill deployment.

---

# Core Domain

## **EvalRunner**

Entry point that coordinates the three eval tiers (rule battery, AI judge, coarse cases) and writes a consolidated report. Module-level functions in `eval.py`; no class wrapper.

### **EvalRunner** << Service >>

Initialisation: module-level functions; no construction required.
------
+ discoverCoarseCases(): List<Path>
	Invariant: must return only case directories that contain an eval.json descriptor; directories prefixed with `_` are excluded
----
+ runRuleBattery(prompt: String, context: dict | None, verbose: Boolean): List<RuleResult>
	Invariant: for every matched rule, pass fixture must exit 0 with 0 violations; fail fixture must exit 1 with exactly 1 violation
	Invariant: only rule directories that have a scanner file, an evals/pass fixture tree, and an evals/fail fixture tree are executed; others are skipped with a warning
	Interaction:
		rules: List<Path> = Assembler.getRules(prompt, context)
		results: List<RuleResult] = []
		for rule_dir in rules:
			result: RuleResult = runSingleRule(ruleDir: rule_dir)
			results.append(result)
		return results
----
+ runAiJudge(prompt: String, context: dict | None, model: String | None, verbose: Boolean, session: AgentSession): List<AiJudgeResult>
	Invariant: every rule with a matching .md file must be judged for both pass and fail fixtures; verdict must equal the expected value ("PASS" for pass fixture, "FAIL" for fail fixture)
	Interaction:
		rules: List<Path> = discoverRules(prompt, context)
		for each rule and fixture_kind in (pass, fail):
			prompt: String = buildJudgePrompt(ruleDir: rule_dir, fixtureKind: fixture_kind)
			agentResult: AgentResult = CursorAgentLauncher.runAgent(session: session, prompt: prompt)
			verdict: String, reason: String = parseJudgeVerdict(stdout: agentResult.stdout)
			results.append(AiJudgeResult(rule, fixture_kind, verdict, reason))
		return results
----
+ runCoarseCases(model: String | None, verbose: Boolean, runDir: Path | None, caseFilter: List<String> | None, coarseJudge: Boolean, session: AgentSession): List<CoarseResult>
	Invariant: actual/ tree is wiped at the start of each case run; only paths listed in expected/ are harvested from the agent workspace; scanners only execute for kinds present in the workspace
	Invariant: coarse AI judge compares expected/ vs actual/ only when all expected files are present and judge is enabled in the descriptor
	Interaction:
		cases: List<Path> = discoverCoarseCases()
		for case_dir in cases:
			workspace: Path = seedWorkspace(caseDir: case_dir)
			agentResult: AgentResult = CursorAgentLauncher.runAgent(session: session, prompt: prompt, workspace: workspace)
			harvestActual(workspaceRoot: workspace, expectedDir: expected_dir, actualDir: actual_dir)
			violations: List<dict> = runAllScanners(scanRoot: scan_root)
			verdict: String, reason: String = judgeCoarseCase(case: case_dir, model: model, session: session)
			results.append(CoarseResult(...))
		return results
----
+ runSeedExpected(model: String | None, verbose: Boolean, runDir: Path, caseFilter: List<String> | None, session: AgentSession): void
	Invariant: existing expected/ tree for each case is wiped before writing; only files with a known extension bucket (.md, .ts, .tsx, .py, .js, .java, .json, .drawio) are written; context/ files are excluded
----
+ main(argv: List<String> | None): Integer
	Invariant: must return 0 only when all executed modes pass; returns 1 on any rule, judge, or coarse failure
	Invariant: coarse and AI-judge modes require a valid AgentSession; missing cursor-agent raises SystemExit
	Interaction:
		args: ParsedArgs = argparse.parse(argv)
		session: AgentSession | None = AgentSessionManager.getOrCreate(sessionFile, storiesRoot, fresh: args.freshSession)
		if mode in (rules, all): report.ruleResults = runRuleBattery(args.prompt, args.context, verbose)
		if mode in (ai-judge, all): report.aiJudgeResults = runAiJudge(args.prompt, args.context, model, verbose, session)
		if mode in (coarse, all): report.coarseResults = runCoarseCases(model, verbose, runDir, cases, coarseJudge, session)
		if mode == seed-expected: runSeedExpected(model, verbose, runDir, cases, session); return 0
		writeReport(report: report, runDir: runDir)
		return 0 if all passed else 1

### references

**Ref — eval.py module**
Source: `stories/src/skill/evals/eval.py`
Locator: module top — lines 1–48 (docstring), 321–371 (rule battery), 600–673 (AI judge), 892–1185 (coarse cases), 1208–1306 (seed expected), 1391–1488 (main)
Extract: partial

```source
Three tiers of eval in one entry point:
  1. `rules`    — Rule battery. For every rule with a scanner + evals/pass + evals/fail,
                  verify pass yields 0 violations and fail yields exactly 1.
  2. `ai-judge` — For every rule, invoke cursor-agent as a judge against the fail fixture.
  3. `coarse`   — For every case under `stories/evals/<case>/`, invoke the agent on a
                  prompt + context, then run every scanner against the merged workspace.
  4. Coarse AI judge (runs inside `coarse` unless `--no-coarse-judge`) — cursor-agent
                  compares `expected/` vs `actual/` per case and returns CLOSE / NOT_CLOSE.
```

### decisions made

- Module-level functions chosen over a class; no state lives between calls — each run mode is fully idempotent and self-contained.
- `_LAST_RUN_DIR` / `_SESSION_FILE` are module constants rather than parameters to keep the CLI surface minimal; callers that need alternate paths pass them explicitly to `run_coarse_cases`.
- AI judge verdict parsing uses two passes: line-by-line JSON first, then regex extraction — to handle cursor-agent streaming formats that embed JSON inside event payloads.
- Coarse judge is gated on `missing == []` — if expected files are absent there is nothing to compare; verdict defaults to NOT_CLOSE with a human-readable reason.
- `discoverRules` delegates to `Assembler.getRules(prompt, context)` rather than scanning the filesystem directly — the assembler infers fidelities and format from prompt+context using the same logic as the generate phase, then scopes to `phase=VALIDATE` (rules only); this keeps rule selection consistent with how the skill itself decides which rules are in play for a given context.

---

## **Report**

Aggregates all results from a single eval run for JSON and text report emission.

### **Report** << ValueObject >>

Initialisation: constructed by `main()` after all mode runs complete.
------
+ startedAt: String
	Invariant: ISO 8601 UTC timestamp captured at the start of `main()`
+ mode: String
	Invariant: must be one of: rules, ai-judge, coarse, all, seed-expected
+ << composition >> ruleResults: List<RuleResult>
+ << composition >> aiJudgeResults: List<AiJudgeResult>
+ << composition >> coarseResults: List<CoarseResult>
----
+ toJsonDict(): dict
	Invariant: must serialise all three result lists using dataclasses.asdict; no fields omitted

### references

**Ref — Report dataclass**
Source: `stories/src/skill/evals/eval.py`
Locator: lines 241–255
Extract: whole

```source
@dataclass
class Report:
    started_at: str
    mode: str
    rule_results: list[RuleResult] = field(default_factory=list)
    ai_judge_results: list[AiJudgeResult] = field(default_factory=list)
    coarse_results: list[CoarseResult] = field(default_factory=list)

    def to_json_dict(self) -> dict:
        return {
            "started_at": self.started_at,
            "mode": self.mode,
            "rule_results": [asdict(r) for r in self.rule_results],
            "ai_judge_results": [asdict(r) for r in self.ai_judge_results],
            "coarse_results": [asdict(r) for r in self.coarse_results],
        }
```

### decisions made

- ValueObject: two Report instances with identical fields represent the same run outcome; no identity tracking needed.
- Report is always overwritten at `stories/evals/last-report.{json,txt}` — no per-run history is kept; the .last-run scratch directory holds per-run workspace artefacts.

---

## **RuleResult**

Outcome of running one rule's scanner against its pass and fail fixtures.

### **RuleResult** << ValueObject >>

Initialisation: constructed by `runRuleBattery()` for each discovered rule.
------
+ rule: String
	Invariant: must equal the rule directory name
+ passOk: Boolean
	Invariant: true only when scanner exits 0 and produces 0 violations against the pass fixture
+ failOk: Boolean
	Invariant: true only when scanner exits 1 and produces exactly 1 violation against the fail fixture
+ passExit: Integer
+ failExit: Integer
+ passViolations: Integer
+ failViolations: Integer
+ error: String | None
	Invariant: set only when the scanner subprocess raised an exception; null when the run completed normally
----
+ ok: Boolean
	Invariant: true only when both passOk and failOk are true; any error sets ok to false

### references

**Ref — RuleResult dataclass**
Source: `stories/src/skill/evals/eval.py`
Locator: lines 192–205
Extract: whole

```source
@dataclass
class RuleResult:
    rule: str
    pass_ok: bool
    fail_ok: bool
    pass_exit: int
    fail_exit: int
    pass_violations: int
    fail_violations: int
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.pass_ok and self.fail_ok
```

### decisions made

- ValueObject: result is immutable once constructed; rerunning the same scanner produces an equal result.
- `fail_ok` requires exit 1 AND exactly 1 violation — a scanner that exits 0 on a bad fixture or produces 2 violations is itself broken and must be fixed before the rule is considered testable.

---

## **AiJudgeResult**

Outcome of one AI judge invocation against a single rule-fixture pair.

### **AiJudgeResult** << ValueObject >>

Initialisation: constructed by `runAiJudge()` for each rule × fixture combination.
------
+ rule: String
	Invariant: must equal the rule directory name
+ fixture: String
	Invariant: must be "pass" or "fail"
+ verdict: String
	Invariant: must be one of PASS, FAIL, ERROR
+ reason: String
	Invariant: one sentence; must not be empty
+ elapsedSeconds: Float

### references

**Ref — AiJudgeResult dataclass**
Source: `stories/src/skill/evals/eval.py`
Locator: lines 208–215
Extract: whole

```source
@dataclass
class AiJudgeResult:
    rule: str
    fixture: str  # "pass" or "fail"
    verdict: str  # "PASS", "FAIL", "ERROR"
    reason: str
    elapsed_seconds: float
```

### decisions made

- ValueObject: each verdict is a self-contained fact about a single judge call; no lifecycle.
- `ERROR` verdict is emitted instead of raising when the agent times out or exits non-zero — this keeps the runner from aborting mid-batch; the caller aggregates errors in the report.

---

## **CoarseResult**

Outcome of one complete coarse eval case run: agent exit, scanner pass/fail, manifest diff, and optional AI judge comparison.

### **CoarseResult** << ValueObject >>

Initialisation: constructed by `runCoarseCases()` after each case completes.
------
+ case: String
	Invariant: must equal the case directory name under stories/evals/
+ agentExit: Integer
	Invariant: 0 means cursor-agent completed without process error; non-zero is surfaced as a violation
+ scannersClean: Boolean
	Invariant: true only when all applicable scanners produce zero violations
+ missingExpectedFiles: List<String>
	Invariant: relative paths under expected/ that were not found anywhere in the agent workspace; empty list means manifest is satisfied
+ extraActualFiles: List<String>
+ << composition >> violations: List<dict>
	Invariant: violations from all scanners, agent stderr tail, and coarse AI judge are merged into one flat list
+ elapsedSeconds: Float
+ aiJudgeVerdict: String
	Invariant: one of CLOSE, NOT_CLOSE, SKIP, ERROR, or empty string when judge did not run
+ aiJudgeReason: String
----
+ ok: Boolean
	Invariant: true only when agentExit is 0, scannersClean is true, missingExpectedFiles is empty, and aiJudgeVerdict is CLOSE, SKIP, or empty
	Interaction:
		judgeOk: Boolean = aiJudgeVerdict in (CLOSE, SKIP, "")
		return agentExit == 0 and scannersClean and missingExpectedFiles is empty and judgeOk

### references

**Ref — CoarseResult dataclass**
Source: `stories/src/skill/evals/eval.py`
Locator: lines 217–237
Extract: whole

```source
@dataclass
class CoarseResult:
    case: str
    agent_exit: int
    scanners_clean: bool
    missing_expected_files: list[str]
    extra_actual_files: list[str]
    violations: list[dict] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    ai_judge_verdict: str = ""  # CLOSE, NOT_CLOSE, SKIP, ERROR
    ai_judge_reason: str = ""

    @property
    def ok(self) -> bool:
        judge_ok = self.ai_judge_verdict in ("CLOSE", "SKIP", "")
        return (
            self.agent_exit == 0
            and self.scanners_clean
            and not self.missing_expected_files
            and judge_ok
        )
```

### decisions made

- `extra_actual_files` is collected but not included in the `ok` predicate — extra files are informational, not blocking; the contract is that every expected file is present, not that no extra files exist.
- `scanners_clean` is computed before adding the AI judge violation so the two failure channels remain distinguishable in the report.

---

# Agent Boundary

### **AgentSession** << Entity >>

+ AgentSession(chatId: String, sessionFile: Path)
------
+ chatId: String
	Invariant: must be a UUID matching the cursor-agent chat identifier; used as `--resume` argument on every subsequent invocation
+ sessionFile: Path
	Invariant: JSON file path where the session is persisted between eval runs
----
+ load(sessionFile: Path): AgentSession | None
	Invariant: returns None when file is absent or contains no valid chat_id; never raises
----
+ save(): void
	Invariant: must write {"chat_id": chatId} to sessionFile; creates parent directories if missing
----
+ getOrCreate(sessionFile: Path, workspace: Path, fresh: Boolean): AgentSession
	Invariant: when fresh is false and a valid session file exists, returns the existing session without creating a new chat; when fresh is true or no session file exists, creates a new chat via CursorAgentLauncher and persists it
	Interaction:
		if not fresh:
			existing: AgentSession | None = AgentSession.load(sessionFile)
			if existing is not None: return existing
		chatId: String = CursorAgentLauncher.createChat(workspace: workspace)
		session: AgentSession = new AgentSession(chatId: chatId, sessionFile: sessionFile)
		session.save()
		return session

### references

**Ref — AgentSession dataclass**
Source: `stories/src/skill/evals/cursor_agent.py`
Locator: lines 87–120
Extract: whole

```source
@dataclass
class AgentSession:
    chat_id: str
    session_file: Path

    @classmethod
    def load(cls, session_file: Path) -> "AgentSession | None":
        ...

    def save(self) -> None:
        ...

def get_or_create_session(session_file: Path, workspace: Path, *, fresh: bool) -> AgentSession:
    ...
```

### decisions made

- Entity: each session has a stable chat_id that identifies a specific cursor-agent conversation; two sessions with the same chat_id are the same session.
- Session reuse avoids cold-start latency on every case in a batch run; `--fresh-session` flag forces a new chat when the session is corrupt or the user wants a clean context.

---

### **AgentResult** << ValueObject >>

Initialisation: returned by `CursorAgentLauncher.runAgent()`.
------
+ exitCode: Integer
	Invariant: 0 means the agent process completed without error; non-zero surfaces as a coarse case violation
+ stdout: String
	Invariant: assembled from narrative event blocks in the stream-json output; falls back to raw line buffer when no narrative events are emitted
+ stderr: String
+ elapsedSeconds: Float
----
+ ok(): Boolean
	Invariant: true only when exitCode is 0

### references

**Ref — AgentResult dataclass**
Source: `stories/src/skill/evals/cursor_agent.py`
Locator: lines 123–131
Extract: whole

```source
@dataclass(frozen=True)
class AgentResult:
    exit_code: int
    stdout: str
    stderr: str
    elapsed_seconds: float

    def ok(self) -> bool:
        return self.exit_code == 0
```

### decisions made

- Frozen ValueObject: result is immutable; identity is irrelevant — two identical results represent the same agent outcome.
- `stdout` is parsed from stream-json narrative events, not raw process stdout — this filters out noise tool-call lines so verdict parsers can reliably extract the agent's response text.

---

### **CursorAgentLauncher** << Service >>

Wraps the `cursor-agent` CLI subprocess. Provides authentication checks, chat creation, and agent invocation with streaming output parsing.

Initialisation: module-level functions; no construction required.
------
+ resolveLauncher(): String | None
	Invariant: returns the full path to the cursor-agent executable; returns None when not on PATH
----
+ assertAuthenticated(): String
	Invariant: raises NotAuthenticatedError when cursor-agent is not on PATH or returns non-zero from `cursor-agent status`
----
+ createChat(workspace: Path): String
	Invariant: must return a UUID matching the chat id pattern; raises RuntimeError when no UUID is found in the command output
----
+ runAgent(session: AgentSession, prompt: String, workspace: Path, timeoutSeconds: Integer, model: String | None, echo: Boolean, extraEnv: dict | None): AgentResult
	Invariant: long prompts (> 4096 chars) are written to a temp file in the workspace to avoid Windows command-line length limits; the temp file is deleted after the process exits
	Invariant: process stdout is parsed as stream-json; narrative text is extracted from assistant message content blocks; raw lines are preserved as fallback
	Invariant: raises subprocess.TimeoutExpired when the agent exceeds timeoutSeconds; raises FileNotFoundError when cursor-agent is not on PATH
	Interaction:
		launcher: String = resolveLauncher()
		args: List<String> = buildArgs(session: session, workspace: workspace, model: model)
		promptFile: TempFile | None = writePromptFileIfLong(prompt: prompt, workspace: workspace)
		proc: Popen = subprocess.Popen(args, stdout=PIPE, stderr=PIPE)
		threads: List<Thread> = [readStdoutThread(proc), readStderrThread(proc)]
		exitCode: Integer = proc.wait(timeout: timeoutSeconds)
		stdout: String = assembleNarrative(narrativeParts, rawLines)
		return new AgentResult(exitCode, stdout, stderr, elapsed)

### references

**Ref — run_agent function**
Source: `stories/src/skill/evals/cursor_agent.py`
Locator: lines 439–587
Extract: partial

```source
def run_agent(
    session: AgentSession,
    prompt: str,
    workspace: Path,
    *,
    timeout_seconds: int = 900,
    model: str | None = None,
    on_stdout: Callable[[str], None] | None = None,
    on_stderr: Callable[[str], None] | None = None,
    on_narrative: Callable[[str], None] | None = None,
    on_tool: Callable[[str], None] | None = None,
    echo: bool = False,
    extra_env: dict[str, str] | None = None,
) -> AgentResult:
```

**Ref — NotAuthenticatedError**
Source: `stories/src/skill/evals/cursor_agent.py`
Locator: line 36
Extract: whole

```source
class NotAuthenticatedError(RuntimeError):
    """Raised when cursor-agent has no valid session."""
```

### decisions made

- `NotAuthenticatedError` is a distinct type (not `RuntimeError`) so callers can distinguish authentication failures from other runtime errors and surface a targeted message.
- Streaming uses two threads (stdout / stderr) rather than `communicate()` so the heartbeat thread can emit progress ticks without blocking on process completion.
- Tool-call events are parsed and forwarded to `skill_trace` for structured run logs; glob/grep/search tool calls are filtered as noise before logging.

---

### **SkillDeployer** << Service >>

Syncs the `stories/` source tree to `.cursor/skills/stories/` before an eval run so cursor-agent loads the developer's latest skill, not a stale snapshot.

Initialisation: module-level functions; no construction required.
------
+ deployStoriesSkill(): Path
	Invariant: existing .cursor/skills/stories/ tree is completely replaced on every call; no merge or incremental copy
	Invariant: coarse-eval cases (stories/evals/), rule fixture data (rules/*/evals/), __pycache__, and .pytest_cache are never deployed
	Interaction:
		if _STORIES_DEPLOY exists: shutil.rmtree(_STORIES_DEPLOY)
		_STORIES_DEPLOY.mkdir()
		for source in _STORIES_SOURCE.rglob("*"):
			if isExcluded(relative: source.relative_to(_STORIES_SOURCE)): continue
			copy source → _STORIES_DEPLOY / relative
		return _STORIES_DEPLOY

### references

**Ref — deploy_stories_skill function**
Source: `stories/src/skill/evals/deploy.py`
Locator: lines 25–47
Extract: whole

```source
def deploy_stories_skill() -> Path:
    """Copy stories/ to .cursor/skills/stories/, replacing the previous deploy.

    Excludes coarse-eval cases and per-rule fixture data — the deployed skill
    ships rule.md and scanner.py but not evals/pass|fail data.
    Returns the deploy destination path.
    """
    if _STORIES_DEPLOY.exists():
        shutil.rmtree(_STORIES_DEPLOY)
    _STORIES_DEPLOY.mkdir(parents=True, exist_ok=True)
    ...
    return _STORIES_DEPLOY
```

### decisions made

- Full wipe-and-replace rather than incremental sync — eval correctness depends on the deployed skill exactly matching source; partial updates would leave stale files from deleted rules.
- Fixture data is excluded from the deployed skill because cursor-agent should not read eval pass/fail fixtures during a run; the deployed skill ships rule.md and scanner.py only.
