# Generate at stories-acceptance-tests hands over one template, Clean Engineering's Python class template, whether Python or TypeScript is chosen, and none for the story test files it tells the agent to save

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Deliver Work With Context Guidance", Produce Formal Artifacts; no scenario covers the template generate gives for acceptance tests in each format.
- **Module and class:** `cdd_guidance/actions/generate/generate.py` and `harness/guidance/guidance.py` (the template of the active format; the `clean_engineering: code` companion of `acceptance_tests` in `cdd_guidance/practices/stories/stories.md`).
- **Severity:** misleading message (the agent is given the wrong language's template and no shape for four or five of the files)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh a3.json`; the two answers are kept as `drv\gen3.txt` and `drv\gen4.txt`).

1. `fidelity-session-output.choose_format {"session": "main", "practice": "stories", "fidelity": "acceptance_tests", "format": "python", "is_chosen": true}`, then `generate.generate {"guidance": "stories-acceptance-tests"}`.
2. Unchoose `python`, choose `typescript` (the answer shows `"chosen_formats": ["typescript"]`), then the same generate.

## Expected
As at `stories-scenarios`, where the template follows the chosen format (the markdown, Python and TypeScript scenario templates each came back for their format): a TypeScript template when TypeScript is chosen, and a shape for each file the save line names (`.story.shared`, `.story.domain.spec`, `.story.server.spec`, `_story.test`, `.story.ui.spec`).

## Actual
Both answers are the same but for the session's format list (67,283 and 67,347 characters). Each holds one `#### Template`, which starts `# Conceptual Clean Engineering Reference (Python style)` and shows `class I{ClassName}(ABC)`, a production class family. With TypeScript chosen it is still the Python one. Neither answer holds a template for a story test: `with story(` appears only inside rule text. The save line then names four Python and five TypeScript files to write.

Smaller, in every Stories generate answer: the schema printed under "Guide this action so the output conforms to this schema" says of a story `scenarios count 1..4; more than 4 and the story is huge`, while the rule `story-scenarios-at-most-seven` in the same answer says at most 7 and that a story with none passes.

## Tier that should catch it
Unit (`generate_spec.py`): no example asks for acceptance tests with TypeScript chosen and checks the template's language.
