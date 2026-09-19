---
name: scout-app
description: >-
  Phase 0 scout: capture 10-20 representative pages from the application.
  surface: 'web' | 'desktop' | 'api'.
  capture_repo: where to write sandbox/extracted-context (blank = repo_path).
  base_url: e.g. 'http://localhost:3000' — auto-detected if blank.
  entry_points: URL paths to visit, e.g. ['/', '/login', '/dashboard'].
      Defaults to ['/'] when blank.
  Writes per page: screenshot.png and aria.yaml under
      sandbox/extracted-context/app-extraction/pages/<slug>/.
  Writes extraction-overview.md at
      sandbox/extracted-context/app-extraction/extraction-overview.md.
  Returns ScoutResult with overview_path, pages_dir, and page_captures.
---

Phase 0 scout: capture 10-20 representative pages from the application.
surface: 'web' | 'desktop' | 'api'.
capture_repo: where to write sandbox/extracted-context (blank = repo_path).
base_url: e.g. 'http://localhost:3000' — auto-detected if blank.
entry_points: URL paths to visit, e.g. ['/', '/login', '/dashboard'].
    Defaults to ['/'] when blank.
Writes per page: screenshot.png and aria.yaml under
    sandbox/extracted-context/app-extraction/pages/<slug>/.
Writes extraction-overview.md at
    sandbox/extracted-context/app-extraction/extraction-overview.md.
Returns ScoutResult with overview_path, pages_dir, and page_captures.

Use MCP tool: `context-setup.scout_app(repo_path: 'str', surface: 'str' = 'web', base_url: 'str' = '', capture_repo: 'str' = '', entry_points: 'Optional[list[str]]' = None)`
