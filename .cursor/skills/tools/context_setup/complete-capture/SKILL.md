---
name: complete-capture
description: >-
  Phase N: capture specific missing or failed pages and update extraction-overview.md.
  missing_pages: list of URL paths or slugs to (re-)capture.
  surface: 'web' | 'desktop' | 'api'.
  capture_repo: where to write sandbox/extracted-context (blank = repo_path).
  base_url: e.g. 'http://localhost:3000' — auto-detected if blank.
  Writes screenshot.png and aria.yaml for each page under
      sandbox/extracted-context/app-extraction/pages/<slug>/.
  Updates extraction-overview.md with the new page sections.
  Returns CaptureResult with added_captures and updated overview path.
---

Phase N: capture specific missing or failed pages and update extraction-overview.md.
missing_pages: list of URL paths or slugs to (re-)capture.
surface: 'web' | 'desktop' | 'api'.
capture_repo: where to write sandbox/extracted-context (blank = repo_path).
base_url: e.g. 'http://localhost:3000' — auto-detected if blank.
Writes screenshot.png and aria.yaml for each page under
    sandbox/extracted-context/app-extraction/pages/<slug>/.
Updates extraction-overview.md with the new page sections.
Returns CaptureResult with added_captures and updated overview path.

Use MCP tool: `context-setup.complete_capture(repo_path: 'str', missing_pages: 'list[str]', surface: 'str' = 'web', capture_repo: 'str' = '', base_url: 'str' = '')`
