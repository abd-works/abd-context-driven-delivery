---
name: context-setup-smoke-test
description: >-
  Test that the application at repo_path is reachable on its primary screens.
  surface: 'web' | 'desktop' | 'api'.
  capture_repo, base_url, and entry_paths are instance fields (blank capture_repo = repo_path;
  blank base_url auto-detects common ports; blank entry_paths defaults to ['/']).
  Appends smoke-test results to tests/stubs/stub-inventory.md under capture_repo.
  Returns SmokeTestResult. passed=True when every probed path returns HTTP 2xx/3xx.
---

Test that the application at repo_path is reachable on its primary screens.
surface: 'web' | 'desktop' | 'api'.
capture_repo, base_url, and entry_paths are instance fields (blank capture_repo = repo_path;
blank base_url auto-detects common ports; blank entry_paths defaults to ['/']).
Appends smoke-test results to tests/stubs/stub-inventory.md under capture_repo.
Returns SmokeTestResult. passed=True when every probed path returns HTTP 2xx/3xx.

Use MCP tool: `context-setup.smoke_test(repo_path: 'str', surface: 'str' = 'web')`
