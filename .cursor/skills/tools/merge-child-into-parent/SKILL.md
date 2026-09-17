---
name: merge-child-into-parent
description: "Roll a completed child result into its parent."
disable-model-invocation: true
---

Roll a completed child result into its parent.

        Close and archive the child while preserving the sub-issue relationship.

Use MCP tool: `workflow.merge_child_into_parent(child: 'str', summary: 'str', workspace: 'str' = '') -> 'dict[str, str | int]'`
