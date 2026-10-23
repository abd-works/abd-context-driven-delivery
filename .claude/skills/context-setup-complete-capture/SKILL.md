---
name: context-setup-complete-capture
description: >-
  Phase N: capture specific missing or failed pages and update extraction-overview.md.
  missing_pages: list of URL paths or slugs to (re-)capture.
  surface, capture_repo, and base_url are instance fields (surface default 'web';
  blank capture_repo = repo_path; blank base_url auto-detects).
  Writes screenshot.png and aria.yaml for each page under
      sandbox/extracted-context/app-extraction/pages/<slug>/.
  Updates extraction-overview.md with the new page sections.
  Returns CaptureResult with added_captures and updated overview path.
---

Phase N: capture specific missing or failed pages and update extraction-overview.md.
missing_pages: list of URL paths or slugs to (re-)capture.
surface, capture_repo, and base_url are instance fields (surface default 'web';
blank capture_repo = repo_path; blank base_url auto-detects).
Writes screenshot.png and aria.yaml for each page under
    sandbox/extracted-context/app-extraction/pages/<slug>/.
Updates extraction-overview.md with the new page sections.
Returns CaptureResult with added_captures and updated overview path.

Use MCP tool: `context-setup.complete_capture(repo_path: 'str', missing_pages: 'list[str]')`
