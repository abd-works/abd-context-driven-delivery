# session.toggle_guidance answers success for a format, practice or stage that is not there

- **Title:** `session.toggle_guidance` with a name no chip, practice or stage has (`drawio`, `Markdown`, `Stories`, `Discovery`, `astrology`, empty) changes nothing, raises the selection's version and answers as if the press landed; `ticket.choose_formats` refuses the same `drawio` by name.
- **Charter:** C1. **Tester:** Pip.
- **Story:** choose-session-practices-and-overlays-in-chat-bar; filter-files-in-files-app. No scenario covers a wrong name on toggle_guidance; the sibling tools refuse one: "Refuse a name that is no pattern" (overlays) and `ticket.choose_formats` ("A label no chip has, such as drawio, ... is refused with FormatNotOfferedError").
- **Module and class:** `space/session/practices/guidance_selection.py`, `GuidanceSelection.toggle` and `_toggled`: an unknown name is appended to the selected list, then `select` drops it (format groups are matched by label, practices by key, stages by `STAGES.names`), writes the record and calls `changed()`. Only an unknown *part* is refused (`UnknownSelectionPart`).
- **Severity:** misleading message.

## Steps

Same sandbox and driver as pip-1 (`scratchpad/et/chips/sandbox/scripts/t5.py`, `t6.py`).

1. `session.toggle_guidance(session=".sessions/chips-ticket/session.json", part="format", name="drawio")`
2. The same with `part="practice", name="Stories"`, `part="stage", name="Discovery"`, `part="format", name="astrology"`, `part="format", name=""`.
3. Compare `session.guidance_selection` before and after; compare `ticket.choose_formats(ticket="chips-ticket", fidelities=["stories-story-map"], label="drawio", is_chosen=True)`.

## Expected

A name that is no chip, practice or stage is refused by name and the record is left alone, as `choose_formats` and `choose_overlays` do; a capitalised spelling (`Stories`, `Discovery` - the stage's title as the board heads it) either works or is refused.

## Actual

Every call answers the selection with the version raised by one (v29 -> v32) and the selection unchanged; session.json is rewritten each time. `choose_formats` on the same label: `FormatNotOfferedError stories-story-map offers no 'drawio' chip: it offers diagram, markdown`. An agent calling toggle_guidance with a format (drawio) or a title (Discovery, which `stages[].title` gives) gets "done", and every page following `guidance_selection_after` wakes and redraws for nothing.

## Tier that should catch it

Unit (`space/session/session_spec.py`): toggle with an unknown name of each part. The spec covers only the unknown part.

## Triage

- **Status:** confirmed. **Severity:** misleading message. **Triaged by:** Latch.
- Reproduced in a unit example on a throwaway session: `toggle_guidance("format", "drawio")`, `("practice", "Stories")` and `("stage", "Discovery")` changed nothing, wrote session.json and raised the version. A capitalised title is refused rather than accepted: every caller (chat bar `chat-bar-view.tsx`, Files app `files-page-view.tsx`) sends the stage's name, the practice's key and the group's label, and `ticket.choose_formats` refuses by name too.

## Fix

- **Scenario:** Refuse a format press no chip stands for (`story_tests/move-work-forward-from-chat-bar/generate-fidelity-outputs-in-chat-bar/generate_fidelity_outputs_in_chat_bar_story.test.md`, story Choose Format).
- **Test (unit):** `space/session/session_spec.py`, a session's guidance selection › that has Discovery and Stories selected › that has a name pressed that no chip, practice or stage has (four examples: format drawio refused naming the chips, practice Stories refused, stage Discovery refused, version left as it was). Seen failing (no exception raised; version raised), then passing.
- **Fix:** `space/session/practices/guidance_selection.py`: new `UnknownSelectionName` (part, name, the names offered); `GuidanceSelection._toggled` reads what the part offers inside the held change and refuses a name it does not offer before anything is written, so the version is not raised. The chat bar shows the refusal through `shownAsFailure` as it does any failed press.
- **Commit:** see below.
