# harness/.context/editor-apps

The clean-engineering model of the increment Integrate Practice Content Editor Apps: what the chat bar's app status row, its file viewer, the Story UI editor, the Graph app and the CDD Kanban need from the Python domain to open each app, edit a story map, and follow the ticket's scope. It is a specification, not code: each file here is the delta of a class family that lives in a real module, named on its first line.

- **Purpose:** Hand implementation the classes, operations, invariants and interactions the increment's scenarios need, reusing the existing classes.
- **Seam (terms):** App, AppStatus, AppNotStarted, AppNotRegistered (harness/installation); ServerHealth.apps; PracticeGuidance.editor, PracticeGuidance.session_root; Graph.load_practice_roots; Session.design_view; FidelitySessionOutput.chosen_formats, choose_format, FormatNotOffered; Ticket.choose_formats; FidelityProgress.editor; FormatChoice.is_chosen; StoryNode.load, rename, move_before, remove; StoryModel.load, show, open_in_session, save; OpenedStoryMap; StoryNodeNotFound; Epic.new_epic, new_story; Story.new_scenario; Scenario.new_step; Step.edit_text; StoryMapEditRefused
- **Dependencies (one-way):** the modules the families belong to keep their own one-way order (`harness/.context/module-context.md`): installation below diagnostics, guidance and graph; space/session and space/kanban above harness; cdd_guidance/practices/stories above harness and below space.

## Constraint

The canonical document is `.context/editor-apps-model.md`; the python files mirror it. When implementation lands a class, its real module's card and model document take over and the entry here is removed.
