---
name: document
description: "document"
disable-model-invocation: true
---

# document

Run this action for any provided context tools, or on the context in general.

Document existing state for provided context tools.

document

With a straight prompt passed, run this action on the context in general. If you took a context tool from the context and not a straight prompt, confirm the use of the context. AskQuestion constrained to the context tools: agent-bdd | bdd | car | cdd | clean-engineering | create-context-tool | ddd | harness | stories | ux | use existing context only.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Use MCP tool: `document.document(tools: 'list', paths: 'list[str]') -> 'str'`
