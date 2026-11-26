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
