Test that the application at repo_path is reachable on its primary screens.
surface: 'web' | 'desktop' | 'api'.
capture_repo: where to write tests/stubs (blank = repo_path).
base_url: e.g. 'http://localhost:3000' — auto-detected from common ports if blank.
entry_paths: URL paths to probe, e.g. ['/', '/login', '/dashboard'].
    Defaults to ['/'] when blank.
Appends smoke-test results to tests/stubs/stub-inventory.md under capture_repo.
Returns SmokeTestResult. passed=True when every probed path returns HTTP 2xx/3xx.

Use MCP tool: `context-setup.smoke_test(repo_path: 'str', surface: 'str' = 'web', base_url: 'str' = '', capture_repo: 'str' = '', entry_paths: 'Optional[list[str]]' = None)`
