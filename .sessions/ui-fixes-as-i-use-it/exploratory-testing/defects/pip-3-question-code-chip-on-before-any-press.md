# Question: the code chip shows selected and filters files before anyone pressed it

- **Title:** On a fresh session, choosing the Specification stage shows the code chip already selected (from the fidelities' default formats), so the file list at once hides the story map's markdown and the class model's markdown, though the person pressed no format chip.
- **Charter:** C1. **Tester:** Pip.
- **Story:** filter-files-in-files-app (Filter Files By Format In Files App); see-work-in-chat-bar. No scenario says what a session that never pressed a chip filters by.
- **Module and class:** `space/session/practices/guidance_selection.py` `FormatGroup.is_selected` (chosen while every offering fidelity has a format of the group chosen; a fidelity with no saved formats answers its default, so the code group - scenarios python, mockup html, model python, all defaults - counts as chosen), and `space/session/practices/file_listing.py` `FileListing.formats`, which filters by every selected group.
- **Severity:** question.

## Steps

Sandbox as in pip-1 (fresh `session.json` with stories, clean_engineering, ux enabled, no `guidance` and no `fidelities` saved; ticket stage Discovery).

1. `session.guidance_selection` -> chips diagram off, markdown off (Discovery only).
2. `session.toggle_guidance(part="stage", name="specification")`.
3. `ticket.root_files(ticket="chips-ticket")`, the `is_listed` files.

## Expected

Unclear, hence the question. FileListing's own rule says "none selected, every format is listed", and the person has selected none; so either no chip should show selected until pressed, or the default formats are meant to count as a choice and the chat bar's code chip being lit is the explanation.

## Actual

After step 2 the answer is `('code', True, ['python', 'html'])` with diagram, markdown and canvas off, and the listing is only `.context/story-map.whiteboard`, `design-canvas/.../canvas.json` (listed for their links) and `ordering/*.py`. `.context/story-map.md`, `.context/story-map.drawio` and `ordering/.context/ordering-model.md` are hidden. In Discovery alone no chip was lit (story map's default markdown is not shared by ux-ia), so adding a stage switches a filter on: which chips light up depends on whether every fidelity in the new set happens to share a default group.

## Tier that should catch it

Unit, in `practice_session_output_spec.py` / `kanban_tools_spec.py` once the intended answer is decided.

## Triage

- **Status:** question, answered in part; the rest is a question for the person. **Severity:** question (no behaviour changed). **Triaged by:** Latch.
- **The chip lit before any press works as intended.** `FidelitySessionOutput.chosen_formats` (`space/session/practices/practice_session_output.py`) says that until a person or an action chooses, a fidelity's chosen formats are the project's defaults for it, else its default format, and that this is "what a chip shows picked"; `FormatGroup.is_selected` (`space/session/practices/guidance_selection.py`) lights a chip while every fidelity offering the group has a format of it chosen. The board's action bar does the same (`.context/story-map.md`, Choose Action And Formats: "the default format picked unless that output exists"). So with Specification added, scenarios (python), mockup (html) and the class model (python) all default to code, and the code chip lights; in Discovery alone the story map's markdown is not shared by ux-ia, so no chip lights. Which chips light does depend on whether the covered fidelities share a default group, by that rule.
- **That the lit chip filters the file list is not decided by any source.** `FileListing.formats` (`space/session/practices/file_listing.py`) filters by every group selected, defaults included, and the Files app story (`story_tests/review-generated-work-in-file-viewer/filter-files-in-files-app/filter_files_in_files_app_story.test.md`, story-map entry Filter Files By Format In Files App: "while any is chosen the list shows only those formats' files") reads a chip as a filter without saying what a session that never pressed a chip lists. Question for the person.
- **Recommendation:** keep a chip meaning one thing. Either (a) the file list filters only by groups a person pressed (a press saved in the session, say `guidance.formats`), while the chips an action writes in stay the fidelities' chosen formats; or (b) keep one meaning, chosen formats, and have the Files app say "filtered by code (the default format)" when nothing was pressed so hidden markdown is explained. (a) also answers pip-4, where turning a filter off took a fidelity's only output format away. Until the person decides, nothing changes.
