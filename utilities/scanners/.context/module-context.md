# Scan (scanners)

**Purpose:** Scanner engine plus mergeable toolset-facing `Scan` binding.

**Primary use case:** validate / document / repair call `scan(paths)`; domains override `_scanner_collection`.

**Rationale:** One kit with ScannerCollection — not a separate `utilities/scan/` peer.

**Seam:** Scan; Scanner; ScannerCollection; ScannerReport; Violation

**Public API:** `Scan.scan`; `Scan._scanner_collection`; engine types/helpers

**Dependencies:** (none)

**Mechanism:** Concrete mergeable `Scan` class in the same package as the engine (one test tier — no separate interface). `Scanner.is_skipped_path` skips demo dirs such as `examples/`, except repair fixtures (`faultyAsset` / `repairedAsset`, or files under `faultyAssets/` / `repairedAssets/`) which stay scannable for regression.
