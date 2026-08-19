# Bdd

**Purpose:** Multi-fidelity BDD generator — behavior signatures deepen into development tests, then hand off to CleanEngineering for matching class code. Hosts a Diagnose companion for stuck RED fixes.

**Primary use case:** Satisfy or iterate BDD specs for a module path: lock describe/it hierarchy, fill tests RED→GREEN, call `ce()` for production code, and call `diagnostic().diagnose()` when the same test stays RED after two fix attempts.

**Rationale:** BDD owns the observation hierarchy and test cycle; CleanEngineering owns OO class deepening at the matching fidelity. Diagnose stays a separate tool so the six-phase loop is not inlined into satisfy/iterate markdown.

**Seam:** `Bdd`

**Public API:** constructor (`fidelity`, `format`, `path`, `session`, `workspace`); providers `ce()`, `diagnostic()`; lifecycle actions `generate`, `grill`, `sketch`, `iterate`, `satisfy`, `validate`, `repair`; tools `transform`, `render(format, content)` (calls `transform` from the current format); scan rules discovered from `scanners/` (`missing-spec` plus ported abd-skills rules: `plain-english-only`, `business-readable-language`, `signature-markers`, `no-remaining-signatures`, `observable-behavior`, `layer-isolation`)

**Dependencies:** BaseContextTool (lifecycle); CleanEngineering (lazy via `ce()` / `transform`); Diagnose (lazy via `diagnostic()`)
