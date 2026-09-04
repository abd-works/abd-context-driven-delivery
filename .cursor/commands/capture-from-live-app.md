Capture context memory from a live application at repo_path.
repo_path={repo_path}  capture_repo={capture_repo}  surface={surface} (one of web | desktop | api).
capture_repo is where stubs and scout land (tests/stubs/{system}/, domain/{aggregate}/stubs/{system}/, sandbox/extracted-context).
Blank capture_repo means the same folder as repo_path.
Collaborators (compile-time references): ContextIndex.

Step 1 — Classify External Dependencies (AI judgment, no tool):
Scan the repo at repo_path for third-party call sites, SDK initialisations,
and environment variables holding external URLs. For each candidate, classify
as 'external' (needs a stub) or 'in-scope' (same-repo or peer-repo service — skip).
Produce a Classification Table: service name, file path, symbol, classification, reason.

Complex-stub trigger: if 5 or more distinct external services are found, OR any
dependency requires a domain-shaped stub return (more than 3 fields), STOP and
produce three pre-pass documents before writing any stubs:
  1. tests/stubs/stub-focus-map.md — stub-focus map (not Stories story-map.md)
  2. tests/stubs/acceptance-criteria.md — stub-focus acceptance criteria
  3. tests/stubs/domain-glossary.md — domain term → minimum fields mapping
Write those files under capture_repo (or repo_path if capture_repo is blank).
Only proceed to Step 2 once all three documents are written.

Step 2 — Write External Stubs (AI judgment, no tool):
For each dependency classified as 'external', write a canned neighbor stub under capture_repo.
Global systems (no owning domain): tests/stubs/{system}/.
Domain-owned neighbors: domain/{aggregate}/stubs/{system}/.
Never a domain folder inside tests/.
Write at the outermost boundary — the HTTP client adapter, SDK factory, or module export.
DO NOT stub OAuth token flows, deep SDK internals, or protocol-layer methods.
Record every hardcoded value introduced by each stub.
Write the Stub Inventory to tests/stubs/stub-inventory.md under capture_repo with
one row per stub: service, boundary point (file + symbol), hardcoded values,
BDD step phrase references (When / And / Then).

Step 3 — Smoke Test: call smoke_test(repo_path=repo_path, capture_repo=capture_repo, surface=surface).
If smoke_test_result.passed is False, identify which screens failed, trace the
boundary point from the stub inventory, repair the stub (Step 2), and call
smoke_test again. Do not proceed to Step 4 until passed is True.

Step 4 — Scout App Pages: call scout_app(repo_path=repo_path, capture_repo=capture_repo, surface=surface).
This runs a Phase 0 thin capture (10-20 representative pages or endpoints) under
capture_repo/sandbox/extracted-context/app-extraction/ and
returns a ScoutResult with overview_path, pages_dir, and page_slugs.

Step 5 — Review Capture Coverage (AI judgment):
Read the extraction-overview.md at scout_result.overview_path.
For each captured page, read its aria.yaml under scout_result.pages_dir/<slug>/:
- Does the ARIA represent a real rendered screen for the page's user_intent?
- Are interactive elements (buttons, inputs, links, headings) present and consistent?
- Is the content suspiciously sparse — single heading, one button, loading skeleton?
Emit a verdict per page: PASS | WARN | FAIL.
FAIL and WARN pages need re-capture; note the reason for each.
If all pages PASS: call context_index.embed(segments_paths=[scout_result.pages_dir])
to index the captured content and report capture complete. Stop.
If any pages FAIL or WARN: proceed to Step 6.

Step 6 — Complete App Capture (only when Step 5 found FAIL or WARN pages):
Collect the URLs or slugs of FAIL and WARN pages into missing_pages.
Call complete_capture(repo_path=repo_path, capture_repo=capture_repo, missing_pages=missing_pages,
surface=surface).
After capture, call context_index.embed(segments_paths=[capture_result.overview_path])
to index the updated overview and report all pages captured.

through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: context_setup.context_setup:ContextSetup
action: capture_from_live_app
```
python -m tools run -
