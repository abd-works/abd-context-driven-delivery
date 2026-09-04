# document

Run this action for any provided context tools, or on the context in general.

Document existing state for provided context tools.

document

With a straight prompt passed, run this action on the context in general. If you took a context tool from the context and not a straight prompt, confirm the use of the context. AskQuestion constrained to the context tools: agent_bdd | bdd | car | cdd | clean_engineering | create_context_tool | ddd | stories | ux | use existing context only.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: document.document:Document
action: document
```
.\tools.ps1 run -
