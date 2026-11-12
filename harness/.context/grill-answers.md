# Grill answers

## Cross-aggregate sync

Asked by the lern_domain_driven gate (`ask-cross-aggregate-sync`) while generating the scenarios and model of Integrate Practice Content Editor Apps (2026-11-12). The specification agent ran as a sub-agent and could not ask the person, so this is the proposed answer, **awaiting the person's confirmation**:

- **Story map edit to rendered formats:** synchronous, in one domain operation. `StoryNode.<edit>` calls `StoryModel.save`, which writes the map's own file, renders each chosen format, and refreshes the session's graph before it answers (cdd_web_domain_access `one-line-to-the-domain`). No event, no second store.
- **Chosen formats between the chat bar and the Story UI editor:** one owner, `FidelitySessionOutput.chosen_formats` in session.json; both read it on their next read. No copy in either page (`state-lives-behind-the-tool`).
- **Ticket activation to the Graph app and the Story UI editor:** `Ticket.activate` records `Board.last_activated` in the same call; the apps read it on their next board read (the board already reads every two seconds). No push.
- **App status:** read from the app's folder and ports on every `ServerHealth.report`; nothing is cached.
