# Grill Answers

## Cross-aggregate sync

**Review Files In Viewer — file comments and the chat queue** (the person, 2026-11-12)

- A file comment that has been sent to the chat queue stays in the viewer, beside its line, marked as sent.
- A comment is not sent, then sent, then processed (the person, 2026-11-12). It is processed once the chat's turn that worked on it has ended. Then the viewer shows the file as the agent changed it.
- Clear processed comments removes only the processed ones.
- File comments are kept in the session folder, so they survive a reload of the page.
- So sending a comment changes two things together: the chat queue gets the message (`chat.send`), and the comment is recorded as sent in the session's comments.

## Scope of this pass

**Review Work In Board Files** (the person, 2026-11-12)

- In this pass: Open Session Files From Details, View Files In Rich Viewer, Save Edited File, Add Comment To File Selection, Send File Comments To Chat, Mark File Comment Processed, Show Changed File In Viewer, Clear Processed File Comments (the last three added 2026-11-12).
- Left out: Show AI Changes As Diff (later), and List Ticket Context Files ("done already").

## Cross-aggregate sync: Integrate Practice Content Editor Apps

Asked by the lern_domain_driven gate (`ask-cross-aggregate-sync`) while generating the scenarios and model of Integrate Practice Content Editor Apps (2026-11-12). The specification agent ran as a sub-agent and could not ask the person, so this is the proposed answer, **awaiting the person's confirmation**:

- **Story map edit to rendered formats:** synchronous, in one domain operation. `StoryNode.<edit>` calls `StoryModel.save`, which writes the map's own file, renders each chosen format, and refreshes the session's graph before it answers (cdd_web_domain_access `one-line-to-the-domain`). No event, no second store.
- **Chosen formats between the chat bar and the Story UI editor:** one owner, `FidelitySessionOutput.chosen_formats` in session.json; both read it on their next read. No copy in either page (`state-lives-behind-the-tool`).
- **Ticket activation to the Graph app and the Story UI editor:** `Ticket.activate` records `Board.last_activated` in the same call; the apps read it on their next board read (the board already reads every two seconds). No push.
- **App status:** read from the app's folder and ports on every `ServerHealth.report`; nothing is cached.

## Decisions (2026-11-12, from the person)

- **Where Story UI lives:** the Story UI editor moves from its own repo (`C:/dev/story-ui`) into `cdd_guidance/practices/stories/app`, the way other tools keep an `app` folder (`harness/graph/app`). It is closest to the Stories practice. Its model objects come from the Stories practice: they reuse or shape after the TypeScript model files already in `cdd_guidance/practices/stories/model/typescript` and the Python story model (`story_model.py`) through the generated adapter. This replaces the scenarios agent's proposal of `space/kanban/app`.
- **Cross-aggregate sync (accepted):** a Story UI edit is saved and rendered to the chosen formats in one operation; chosen formats live only in session.json; the other apps read the active ticket on their next read (no push).
- **Session activated last:** do NOT add `Board.last_activated` or any new `_board.json` field. The graph follows the chat's open session (the session `sessions.switch` / activation opened), which already exists.
- **Editor tiles:** every Stories file gets a Story UI editor tile in the file viewer, acceptance-test code files included.
- **Story notes:** the story model gets a description field holding the paragraph under each story (and epic) heading. Story UI's "notes" is renamed to description so the UI matches the model. A save writes descriptions back unchanged, so hand-written story maps (harness/.context/stories/story-map.md) are editable, not read-only.
- **Scenario files:** editable in Story UI (scenarios, steps, examples through the story model).
- **Acceptance-test files:** not edited in Story UI; shown as links that open the file in the chat bar's file viewer.
- **Examples:** examples are already part of the story model. Where Story UI's screens disagree with the model, fix the screens to the model.
- **Increments:** add increments to the story model, shaped as the old Story UI's JSON had them: an ordered list of named increments, each a collection of stories that must exist in the story map. Edited through the model; the Story UI increment views come back on it.
- **Ticket scope:** Story UI opened from the board on a ticket shows only the part of the story map the ticket's session covers.
- **Instant moves (PendingChanges):** keep it. A person's own move shows on the board before the server answers.
- **Graph app named 'Graph':** stays as it is for now; no framework change.
- **Board server's own routes:** opening a Claude chat is core CDD chat communication, so `claude/open` moves out of the board's TypeScript server into the chat module (`harness/chat`), reached through the generated adapter, with a test seam so specs never open real `claude://` links. The board's Update (rebuild its page) reuses `App.install` instead of its own route.

## Decided while implementing the person's decisions (2026-11-12, implementation agent E)

- **Where increments are stored:** in the thin slice beside the story map (`thin-slice.md`, or `thin-slicing.md`, `thin-slices.md`, `increments.md`, as `StoryMapFiles.thin_slicing` finds it), the representation the stories practice already reads (`### Increment N: Name`, its outcome and slicing notes, `- *Story*` bullets). No new store. A markdown story map opened in a session reads it into `StoryModel.increments` (`MarkdownIncrement`) and keeps it as its `slicing`; a save writes it back with every line an edit does not touch, so the hand-written `harness/.context/stories/thin-slice.md` round-trips byte for byte. A story is delivered by one increment at most: `Increment.add_story` takes it off the increment that held it. An increment's description is the text between its heading and its stories label (its outcome and slicing notes). A map that keeps no thin slice (a scenario file) refuses `new_increment`.
- **How a hand-written story map stays editable:** a story map and a scenario file opened in a session are read by themselves through their own format (`StoryModel.opened_from`), not merged with the folder's scenario files. Each outline node keeps the lines it was read with (`OutlineLines`): its heading, written back while it says what the node says (links aside), and the lines under it, its `description`, written back while unchanged; the lines above the first epic are the story map's own description. `harness/.context/stories/story-map.md` saved with no edit is byte-identical (modulo line endings), and a rename changes only that heading.
- **Who owns the ticket's scope:** the story model. `StoryModel.scope` answers the addresses of the map's stories the session it was opened in names (`Session.stories`, through `OpenedStoryMap.session_stories`, read by `stories_named`): the rule of what the ticket covers stays in Python, and the page only draws the part it is sent, with a Ticket scope toggle to see the whole map. A page query was not chosen because it would repeat the session's rule in TypeScript (`domain-lives-in-python`).
- **Acceptance-test links:** `Story.acceptance_tests` lists the session's story tests that hold the story (every file the Stories fidelities declare in the session's checkout, `FidelitySessionOutput.every_file`). The Story UI shows them as links that open the file read only beside the map, through the session's file manager (`SourceViewGenerated`). Open question for the chat bar: the side panel has no channel back to the chat bar's file viewer, so a link cannot open the file there yet.
- **Examples:** the screens now draw a scenario's examples as the story model holds them, one table with a row per example (`Scenario.examples`, from `Examples.table`), read only, since the model has no operation that edits an example; the copied example editing controls (add, remove, reorder rows and fields) had no model behind them and are deleted.
- **`StoryModel.save` is now `write_back`:** a markdown, drawio or code story map is itself the opened map now, and those formats already had a `save` that answers their text, so the opened map's save took a name of its own.

## Decided while closing the three Story UI gaps (2026-11-12, implementation agent F)

- **Acceptance-test links answered:** the open question above (no channel from the side panel back to the chat bar's file viewer) is answered by the chat's own command queue. A link press calls `Chat.send(kind="open_file", text=<path>)` on the chat the Story UI editor was opened beside, named in the page's `?chat=` link (`CHAT_QUERY` in the generated `cdd-shared`; the chat bar's editor tile sets it to its own chat, the board's editor widget to the ticket's working chat). The chat's mod takes it at its next check-in, as it takes every board message, and opens the file in its existing files pane (`openFileInViewer`), never in a viewer of its own. The Story UI no longer reads files (`SourceViewGenerated` and the file manager's routes left its routes); a page no chat opened lists the paths and says where to read them.
- **Example rows edited through the model:** `Example` is a toolset of its own (`example.edit_field`, `example.rename`, `example.remove`), named `{scenario}.example:{slug}`; the column that names an example renames it. A markdown example (`MarkdownExample`) keeps the row it was read from and stands where the row stood, so an untouched row is written back byte for byte and an edited one changes only its edited cells. An example keeps the place its table gives it, so `move_before` is refused, and it has no description, so `edit_description` is not offered. An example named by its place (`example-2`) cannot be removed from the middle of its table, since the rows after it would read back under other names: the save is refused and nothing is written.
- **Epic and sub-epic descriptions on screen:** an epic's or sub-epic's lane, once opened, shows the same description editor a story's card shows, saved through `Epic.edit_description` and written back as a story's is.
