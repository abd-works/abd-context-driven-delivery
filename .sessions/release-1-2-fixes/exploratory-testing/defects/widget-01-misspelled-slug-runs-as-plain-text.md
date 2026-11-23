# A fidelity or practice name spelled any way but its exact lower-case slug is accepted and run as plain text, so the action hands back no rules

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers how a guidance name is read (only `deliver-work-with-overlays` has a scenario file).
- **Module and class:** `harness/guidance_actions/guidance_actions.py`, `GuidanceArgument.text` / `_slug_words` / `_named` (a word that is not an exact slug makes the whole argument "text the action runs once on").
- **Severity:** wrong result (silent: the call succeeds)

## Steps
Session `main` on the sandbox `repo` (Stories on, UX off), through a throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`, calls in `drv\c2.json`):

    generate.generate {"guidance": "stories-story-map"}     -> 25,540 characters, the story map rules
    generate.generate {"guidance": "story_map"}             -> 816 characters, no rules
    generate.generate {"guidance": "Stories-Story-Map"}     -> 824 characters, no rules
    generate.generate {"guidance": "STORIES-STORY-MAP"}     -> 824 characters, no rules
    generate.generate {"guidance": "stories_story_map"}     -> 824 characters, no rules
    generate.generate {"guidance": "stories story map"}     -> 824 characters, no rules
    generate.generate {"guidance": "Story Map"}             -> 816 characters, no rules
    generate.generate {"guidance": "IA"}                    -> 809 characters, no rules (ux is off; "ux-ia" is refused by name)
    generate.generate {"guidance": "wibble-wobble"}         -> 820 characters, no rules
    generate.generate {"guidance": ""} and {"guidance": []} -> 805 characters, no rules, nothing named

## Expected
A name that is one spelling away from a slug (other case, underscores, the fidelity's own name `story_map` that the AGENTS.md table and `ticket` tools show) is either worked on as that fidelity or refused by name with the slugs listed, as `["stories-story-map","stories-nonsense"]` and `ux-ia` already are (`UnknownGuidance`, `GuidanceTurnedOff`). The known history "a slug of a practice turned off ran as plain text so validate checked nothing" is the same failure for these spellings.

## Actual
`isError=False`. The answer is the action's opening sentence, the word as sent, and the closing sentence, e.g.

    Write artifacts for each listed guidance at its current fidelity. ... 
    story_map
    After the artifact is written, call validate ...

No rule, no template, no output folder. An agent reads it as success and writes with no guidance. A single slug-shaped word (`wibble-wobble`, `STORIES-STORY-MAP`) is not prose and could be refused without hurting the "prose still runs once" promise.

## Tier that should catch it
Unit (`harness/guidance_actions/guidance_actions_spec.py`): the argument reading is pure. The specs cover the exact slug, a wrong member of a list, and a turned-off slug, but no other spelling of a real name as a single string.

## Also seen by
- Widget, on render: `render.render {"guidance": "story_map", "format": "drawio", "paths": [".context/story-map.md"], "source": "markdown"}` answers `["story_map"]` with `isError=False` and renders nothing.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on port 48933, on a fresh repository of my own (`C:\dev\_et\sparky\confirm\widget\wz.py`; the report's `drv` files are not in the report). `stories-story-map` answers 25,610 characters with the rules. `story_map`, `Stories-Story-Map`, `STORIES-STORY-MAP`, `stories_story_map`, `stories story map`, `Story Map`, `IA`, `wibble-wobble`, `""` and `[]` each answer 761 to 780 characters with no error: the opening sentence, the word as sent, the closing sentence. My sandbox did not turn UX off, so `IA` was tried with UX on.
- Cause, if you found it: Not read in the code. By what is seen: a word that is no slug is taken as prose for the action instead of being looked up or refused.
- Shares its cause with: widget-02 (how a guidance argument is matched to a practice or fidelity)
