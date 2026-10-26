---
name: context-setup-scout-app
description: >-
  Phase 0 scout: capture 10-20 representative pages from the application.
  surface: 'web' | 'desktop' | 'api'.
  capture_repo, base_url, and entry_paths are instance fields (blank capture_repo = repo_path;
  blank base_url auto-detects; blank entry_paths defaults to ['/']).
  Writes per page: screenshot.png and aria.yaml under
      sandbox/extracted-context/app-extraction/pages/<slug>/.
  Writes extraction-overview.md at
      sandbox/extracted-context/app-extraction/extraction-overview.md.
  Returns ScoutResult with overview_path, pages_dir, and page_captures.
---

Phase 0 scout: capture 10-20 representative pages from the application.
surface: 'web' | 'desktop' | 'api'.
capture_repo, base_url, and entry_paths are instance fields (blank capture_repo = repo_path;
blank base_url auto-detects; blank entry_paths defaults to ['/']).
Writes per page: screenshot.png and aria.yaml under
    sandbox/extracted-context/app-extraction/pages/<slug>/.
Writes extraction-overview.md at
    sandbox/extracted-context/app-extraction/extraction-overview.md.
Returns ScoutResult with overview_path, pages_dir, and page_captures.

Use MCP tool: `context-setup.scout_app(repo_path: 'str', surface: 'str' = 'web')`
