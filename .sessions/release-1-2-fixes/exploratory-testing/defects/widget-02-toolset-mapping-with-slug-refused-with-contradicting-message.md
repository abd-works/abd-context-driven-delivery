# A `{"toolset": "stories", "fidelity": ...}` mapping, the form the tool's schema advertises, is refused with "no practice or fidelity has the slug 'stories'; the slugs are stories, ..."

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `harness/guidance_actions/guidance_actions.py`, `GuidanceArgument._mapped` (raises `UnknownGuidance(toolset, self.slugs)` when toolset is not a `module:Class` ref).
- **Severity:** misleading message

## Steps
Same session and server as widget-01 (`drv\c2.json`):

    generate.generate {"guidance": {"toolset": "stories", "fidelity": "story_map"}}
    generate.generate {"guidance": {"toolset": "ux", "fidelity": "ia"}}        (ux is turned off)
    generate.generate {"guidance": {"foo": "bar"}}

## Expected
The input schema of every guidance action offers `{"toolset": string, "fidelity": string, "context": object}` with no word on what `toolset` holds. An agent fills it with the practice's slug. Either the slug is taken (it names the practice), or the refusal says a toolset is a `module:Class` reference. For `ux` the refusal should be the `GuidanceTurnedOff` one a string gets.

## Actual
    UnknownGuidance: no practice or fidelity has the slug 'stories'; the slugs are stories, stories-story-map, ...
    UnknownGuidance: no practice or fidelity has the slug 'ux'; the slugs are stories, ... (ux not said to be turned off)
    UnknownGuidance: no practice or fidelity has the slug ''; the slugs are ...

The message denies a slug and then lists that same slug first, so the agent cannot tell what to change.

## Tier that should catch it
Unit (`guidance_actions_spec.py`): no example sends a mapping whose toolset is a slug.
