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
