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

## Triage

- **Status:** confirmed. **Severity:** wrong result. **Triaged by:** Latch.
- Reproduced in a unit example on a throwaway session (Stories in Discovery): pressing the markdown chip off wrote `"story_map": {"formats": []}`, the state `choose_format` refuses. `GuidanceSelection._format_fields` took the group's formats away with no last-format check, and `select` wrote the list past `FidelitySessionOutput.choose_formats`.
- Of the two outcomes the report allows, the press now refuses, as `choose_format` does: keeping the format while the chip turns off cannot be drawn, since a chip shows the fidelity's chosen formats (pip-3's triage). Splitting a chip into a file filter and a written format is the person's call, recorded in pip-3.

## Fix

- **Scenario:** Refuse a format press that would leave a fidelity no format (`story_tests/move-work-forward-from-chat-bar/generate-fidelity-outputs-in-chat-bar/generate_fidelity_outputs_in_chat_bar_story.test.md`, story Choose Format).
- **Test (unit):** `space/session/session_spec.py`, a session's guidance selection › that has Discovery and Stories selected › that has the story map's only chosen format pressed off (refused with *LastFormatLeftOut* naming markdown; markdown kept chosen). Seen failing (no exception; `[]`), then passing. The example "should name no format once none is chosen", which pressed that last format off, now reaches no chosen chip the way a person can: Stories and UX in Discovery share no default group.
- **Fix:** `space/session/practices/guidance_selection.py` `_format_fields` raises *LastFormatLeftOut* (from `practice_session_output`) when a group left out would leave a fidelity none; it runs inside the held change, so nothing is written and the version is not raised. The chat bar shows the refusal through `shownAsFailure` ("The markdown format was not changed" and the reason).
- **Commit:** see below.
