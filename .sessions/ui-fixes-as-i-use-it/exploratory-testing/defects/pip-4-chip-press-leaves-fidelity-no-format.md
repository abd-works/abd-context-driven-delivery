# A format chip press leaves a fidelity with no format chosen, which choose_format refuses

- **Title:** Pressing a lit format chip off through `session.toggle_guidance` writes `"formats": []` for a fidelity whose only chosen format was in that group, the state `FidelitySessionOutput.choose_format` refuses as `LastFormatLeftOut`.
- **Charter:** C1. **Tester:** Pip.
- **Story:** see-work-in-chat-bar / filter-files-in-files-app. No scenario covers it; the promise is in `FidelitySessionOutput.choose_formats`: "Refused when leaving them out would leave the fidelity no format chosen (*LastFormatLeftOut*), so it always writes in at least one", and the comment above `chosen_formats` (the chat bar's chips, the board's chips and the Story UI show one choice).
- **Module and class:** `space/session/practices/guidance_selection.py`, `GuidanceSelection._format_fields` (a group left out takes away what each fidelity has chosen from it, with no last-format check) and `select`, which writes the list straight into `fields.practice(p).fidelity(f).formats`, past `choose_formats`.
- **Severity:** wrong result.

## Steps

Sandbox project as in pip-1; a fresh session `.sessions/fresh/session.json` with only stories enabled, nothing saved for its fidelities, ticket stage Discovery (`scripts/t9.py`).

1. `session.guidance_selection(session=".sessions/fresh/session.json")` -> the markdown chip is lit (story_map's default format).
2. `fidelity-session-output.choose_format(session=..., practice="stories", fidelity="story_map", format="markdown", is_chosen=False)` -> refused.
3. `session.toggle_guidance(session=..., part="format", name="markdown")`.
4. Read `session.json`.

## Expected

The chip press either refuses the same way choose_format does, or keeps the fidelity's last format (e.g. the chip turns off as a filter without taking away the fidelity's only format), so a fidelity always writes in at least one format whichever control the person used.

## Actual

Step 2: `LastFormatLeftOut markdown is the only format chosen for story_map; choose another format before leaving it out`.
Step 3 answers v1 with markdown off, and session.json holds `"story_map": {"formats": []}`. `chosen_formats` now answers `[]` ("what a story map edit renders to and what a chip shows picked"), so a story-map edit writes only its own file and the board/Story UI chips show nothing picked for it. The same happened on the bigger session for `ux-ia` (`"ia": {"formats": []}`).

Underneath: a chip on the chat bar is used by people as a *filter* of the file list ("filtering by markdown…"), but the press rewrites which formats each fidelity *writes*, so turning a filter off can take a fidelity's only output format away.

## Tier that should catch it

Unit: a guidance_selection / session spec pressing the only lit chip off and reading the fidelity's chosen formats. Specs check the chips' `is_selected`, not the fidelity record left behind.
