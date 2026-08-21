# host_lifecycle — module context

## Purpose
`HostLifecycle` owns slash commands for core host lifecycle actions that still execute on each context tool: `generate`, `validate`, `document`, and `satisfy`. Each action loops `for host in self.context_tools(tools)` and delegates to the host's matching action.

## Seam
`HostLifecycle`

## Public API
- `generate(tools)`
- `validate(tools)`
- `document(tools, paths)`
- `satisfy(tools)`
