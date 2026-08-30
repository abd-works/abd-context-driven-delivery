# Scan

**Purpose:** Action kit plus scanner engine. `/scan` runs the listed context tool's collection; composed `self.scanner` is bound to that host.

**Primary use case:** validate / document call `self.scanner.scan(paths)`; slash `/scan` passes `arguments.tools`. Domains expose a scanner collection on the host (not a hostless Scan).

**Rationale:** A path-only `scan.scan:Scan` has no rules. What you stand against is the host's scanner collection. The engine lives in this same kit — not a `utilities/scanners/` peer.

**Seam:** `Scan.scan` is `@prompt` plus `@agent_tool`. Slash `/scan` lists context tools. Hosts call `self.scanner.scan(...)` on a Scan bound to `host=self`. `ScannerRunner` is a CLI helper, not a tool or prompt.

**Public API:** `Scan.scan(paths, …, tools=)`; host scanner collection; engine types/helpers (`Scanner`, `ScannerCollection`, `ScanReport`).

Eval Repair (sketch) consumes the scan result as **ScanReport**: `ok`, `matches(mistake)`; overloads `scan(paths)` and `scan(paths, root, rule)`.

**Dependencies:** `lifecycle.LifecycleAction` (slash begin/end); engine types have none.

**Mechanism:** Host association is required to know which scanners run. `Scan.bound_to(host)` (or an explicit `collection=`) binds the rule set. Override the host scanner-collection hook on the context tool. `Scanner.is_skipped_path` skips demo dirs such as `examples/`, except repair fixtures (`faultyAsset` / `repairedAsset`, or files under `faultyAssets/` / `repairedAssets/`) which stay scannable for regression. Paths the caller names in `scan(paths=…)` are also exempt for that call — via `Scanner.explicitly_requested` — so an agent that asks about a fixture is not told it is clean because the path was filtered out.
