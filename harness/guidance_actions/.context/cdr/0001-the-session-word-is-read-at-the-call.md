# The command's words are read once, at the call

A board command names the session it is for in a `session=` word inside its `guidance` argument, such as `/actions-validate ux-mockup session=.sessions/checkout-flow/session.json`. The round-6 review (harness core, row 9) asked for the board's call to carry the ticket instead, so the call opens the ticket's session and no state travels as text.

The word stays. It is read once, where the call arrives: `GuidanceCommand.from_guidance(guidance)` takes it out of the argument, `GuidanceAction.for_call` opens that session through `call.session_named(...)`, and the action holds the session object from then on. Nothing below `for_call` sees the text.

The same holds for the other words a command adds to the guidance, `overlays=` (the pattern overlays the chat bar's command runs with) and `format=` (the formats the session board's command writes in). Until the version-1 refactoring each was read by a function of its own at a different layer (`session_file_named` at the call, `overlays_named` when the work list took the guidance, and the format word again while the slugs were read), so the one string was parsed three times. The version-1 review (`hold-state-on-the-object-not-in-parameters`) flagged that as state parsed back out of a string. Now the three words are read in one place, into one value the action holds (*GuidanceCommand*: the guidance without them, `session_file`, `overlays`, `formats`), and the work list takes that value, so no object below the call reads the text again.

## Why the word stays

- **The command is chat text.** The chat bar and the session board put the command into whichever chat the person sends it to (`harness/chat-ui`, `space/kanban`). That chat's agent calls the MCP tool with the arguments the command shows it; the `guidance` argument is the only channel from the board to the action that every IDE carries.
- **The MCP tools keep their parameters.** Installed skills, commands and agents call `generate.generate(guidance)`, `validate.validate(guidance, ...)` and the rest. A separate `ticket` or `session` parameter on every guidance action changes every installed instruction and every IDE's tool schema; the refactor's rule is that MCP tool names and parameters stay as they are.
- **The text is the process boundary.** The rule against state written into a string is about objects that pass a string among themselves inside the process. Here the string comes from outside the process, is parsed once, and becomes the session object the action holds, which is the same thing the MCP server does with the project header.

## Considered options

- **A `ticket` parameter on every guidance action.** Rejected: it changes every published tool's parameters, and the chat would still have to type the ticket into the call.
- **The board calls the action itself, holding the ticket.** Rejected for now: the agent must run the action in its own chat, with its own tools, so the board cannot run it on the agent's behalf.

## Consequences

- `GuidanceCommand.from_guidance` is the one reader of the command's words; `GuidanceArgument` reads only the guidance it holds, and writes each fidelity in the command's formats it writes.
- The words stay chat text because the story map locks them as what the board and the chat bar write (`.context/story-map.md`, Choose Graph Overlays and the action bar's commands); replacing them with typed tool arguments changes every published action's parameters, the board's and the chat bar's commands, and those scenarios together, and is left to a change of those scenarios.
- A chat that sends no word works in the session open in its project (`call.session`).
- If the board later reaches a chat through a channel that carries structured arguments, the ticket replaces the word in `for_call` alone.
