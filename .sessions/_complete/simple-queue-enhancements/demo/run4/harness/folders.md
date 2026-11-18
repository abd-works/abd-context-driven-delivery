# Harness folders

## agent_tools

- .py files: 18
- Purpose: Turns an ordinary annotated Python class into a toolset of operations an agent can list, run as Python, or follow as written instructions, without hand-written MCP, skill, or hook files.

## annotations

- .py files: 6

## catalog_generator
- Purpose: Renders the CDD catalog, self-contained HTML pages showing every practice, its fidelities and rules, the actions, and the utilities, read straight from the live guidance classes and their markdown.

- .py files: 30

## chat-ui
- Purpose: no module context

- .py files: 0

## chat
- Purpose: Reaches a Claude Code chat from outside it, so the session board can see which chats are connected and send one a command.

- .py files: 4

## design_canvas
- Purpose: Writes a Claude Design canvas as files (its pages, boards, and artboard files tied together by canvas.json), so a practice lays out its artboards and the canvas decides where each file goes.

- .py files: 9

## diagnostics
- Purpose: Reports whether CDD is running and answering: the server health report says which long-running parts are up, and the probes check that what an install published answers through the live host.

- .py files: 28

## e2e_review
- Purpose: no module context

- .py files: 2

## files_app
- Purpose: Shows a session's files beside the chat, as a file viewer app on its own server, and takes a person's comments on them back to that chat.

- .py files: 2

## git
- Purpose: Runs git the same way everywhere, with one set of time limits and one error, so no caller has to stop a hung git or read its exit code.

- .py files: 2

## graph
- Purpose: Reads a working copy (code, specs, story maps, and model documents) into its practices' nodes and edges, so rules can be checked against what is on disk and a person can browse the result in the graph explorer.

- .py files: 52

## guidance
- Purpose: Holds the body of practice an agent follows (overview, guidance, rules, templates, and the instructions that join them) read from markdown beside the class, with each practice deepening through named fidelities.

- .py files: 33

## guidance_actions
- Purpose: The shared start of every action an agent runs on practice guidance (Generate, Validate, Document, Sketch, Partition), made per call for that call's session and run once for each guidance listed.

- .py files: 3

## hooks
- Purpose: Lets a toolset member run when the IDE fires a named event such as sessionStart or preToolUse, merging every handler's answer into one reply, and publishes those hooks through the hook server.

- .py files: 10

## installation
- Purpose: Publishes every annotated toolset member in a repository into an IDE's folder (.claude, .cursor, .github, Kilo) so no author writes a skill, command, rules file, MCP entry, or hook entry by hand.

- .py files: 25

## markdown

- .py files: 8

## mcp

- .py files: 33

## process

- .py files: 11

## whiteboard

- .py files: 3

