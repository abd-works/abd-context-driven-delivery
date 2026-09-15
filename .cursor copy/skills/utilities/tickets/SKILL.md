---
name: tickets
description: "Manage project tickets from {{request}}."
disable-model-invocation: true
---

Manage project tickets from {{request}}.

        Start by calling read_ticket_rules and follow every rule it returns; the repo's
        rules override defaults. Display each available ticket tool name and purpose
        before acting. Call list_project_statuses when you need the board columns.
        Then review ticket statuses so board state and left-to-right column order are
        known. Then call only the tool needed to move a ticket, add a
        child ticket, merge a completed child into its parent, update a ticket, update
        labels, align children to parent, or report board status. Never infer a ticket
        number when the request is ambiguous.

Use MCP tool: `workflow.manage_tickets(request: 'str', workspace: 'str' = '') -> 'str'`
