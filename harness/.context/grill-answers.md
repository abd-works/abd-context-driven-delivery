# Grill answers

## Cross-aggregate sync

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
