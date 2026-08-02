# sub_agent — module context

## Purpose
`sub_agent` provides the `@sub_agent` decorator and `SubAgentTool` dataclass that together mark a toolset method as a non-blocking background sub-agent launch. When the decorator is applied on top of `@tool`, it sets `_is_sub_agent = True` and suppresses `_is_tool` so the standard tool-discovery path skips it; `discover_sub_agent_tools` picks it up instead and produces `SubAgentTool` objects whose `signature_entry` renders as `kind: sub_agent / launch: non_blocking` in the manifest.

## Seam
`SubAgentTool`, `sub_agent`, `discover_sub_agent_tools`

## Dependencies
`tools.tool`

## Mechanism
Decorator stacking — `@tool` runs first to capture the signature; `@sub_agent` then flips the routing flags so the method surfaces in the manifest with sub-agent semantics rather than inline-tool semantics.
