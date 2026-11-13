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
