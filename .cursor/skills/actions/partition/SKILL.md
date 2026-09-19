---
name: partition
description: >-
  Split the given context into an index plus verbatim segments for each listed Guidance host. Fail if any new chunk misses a named entry the index required. Pass a string to partition that text once.
---

Split the given context into an index plus verbatim segments for each listed Guidance host. Fail if any new chunk misses a named entry the index required. Pass a string to partition that text once.

Use MCP tool: `partition.partition(guidance: 'GuidanceArg', context: 'str', mode: 'str' = 'one_go', out_root: 'str | None' = None)`
