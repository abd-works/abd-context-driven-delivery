# validate

Run this action for any provided context tools, or on the context in general.

Validate artifacts for provided context tools.

validate

If you took guidance from the context and not a tool, confirm the use of the context. AskQuestion constrained to the context tools: agent_bdd | bdd | cdd | clean_engineering | create_context_tool | ddd | stories | ux | use existing context only.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: validate.validate:Validate
action: validate
```
python -m tools run -
