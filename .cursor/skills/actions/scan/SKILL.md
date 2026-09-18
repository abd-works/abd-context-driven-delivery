Run the listed Guidance hosts' mechanical scanners on the given paths and report potential violations. Fix the source that failed the rule; do not patch the scanner to make the report green. Pass a string to scan once with the bound collection.

Use MCP tool: `scan.scan(paths: 'list[str]', root: 'str | None' = None, rule: 'str | None' = None, guidance: 'GuidanceArg | None' = None)`
