# validate's `rule` argument cannot be used by an agent: a rule's name is refused by the schema, and an object passes the schema and fails with AttributeError

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers validating one rule.
- **Module and class:** `cdd_guidance/actions/validate/validate.py`, `Validate.validate` (`rule: Rule | None`) and `_report` / `_rules_text`; the MCP input schema publishes `rule` as `{"anyOf": [{"type": "object"}, {"type": "null"}]}`.
- **Severity:** wrong result (the argument the tool describes never works on the server)

## Steps
Session `main` on the sandbox `repo`, throwaway cdd server (`drv\run.py`, calls in `drv\c3.json`, `drv\c4.json`):

    validate.validate {"guidance": "stories-story-map", "rule": "verb-noun-format", "paths": [".context/story-map.md"]}
    validate.validate {"guidance": "stories-story-map", "rule": "no-such-rule", "paths": [".context/story-map.md"]}
    validate.validate {"guidance": "stories-story-map", "rule": {"name": "verb-noun-format"}, "paths": [".context/story-map.md"]}

## Expected
The tool says "rule: one Rule to check. Omit it to walk each guidance's rules." A rule is known to an agent only by its name (`verb-noun-format`, as the report and the rules print it), so the name checks that one rule, and a name no rule has is refused by name.

## Actual
    Input validation error: 'verb-noun-format' is not valid under any of the given schemas
    Input validation error: 'no-such-rule' is not valid under any of the given schemas
    RecipeLineFailed: Validate.validate recipe line ...validate.py:64 `report = self._report(rule, graph_named=bool(graph))` failed: AttributeError: 'dict' object has no attribute 'validate'

A real rule and a made-up one get the same refusal, which names neither the rule nor the form wanted. The only value the schema lets through is an object, which no code turns into a Rule.

## Tier that should catch it
Heavy (`validate_heavy_spec.py`, through the server): no example passes `rule`; the unit spec passes a Rule object in process, which a chat cannot send.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on port 48933, on a fresh repository of my own (`C:\dev\_et\sparky\confirm\widget\wz.py`; the report's `drv` files are not in the report). `rule: "verb-noun-format"` and `rule: "no-such-rule"` both answer `Input validation error: '...' is not valid under any of the given schemas`; `rule: {"name": "verb-noun-format"}` answers `RecipeLineFailed ... validate.py:64 ... AttributeError: 'dict' object has no attribute 'validate'`.
- Cause, if you found it: `cdd_guidance/actions/validate/validate.py` `Validate.validate` hands `rule` to `self._report` as given; the tool's schema lets only an object through, and nothing turns a name or an object into a Rule.
- Shares its cause with: widget-10 (an argument of validate that the tool describes and the code does not carry out)
