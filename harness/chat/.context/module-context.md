# harness/chat
*Chat* is a Claude Code chat reached from outside it, so the session board can see which chats are connected and send one a command. A chat is connected while its cdd-board mod checks in every second; `Chat.load(chat)` is the chat with that id, and `chat.list` lists the connected ones with their name, whether a turn is running, and the folder they work in.

*ChatCommand* is a command a chat takes at its check-in: submit a prompt, fill the prompt box, or run a slash command. *ChatMessage* is a command as the board lists it — when it was sent and where it stands (waiting, taken, shown, done, or failed, with the reason it failed).

`chat.open(folder, prompt)` opens a new chat in the Claude app on a folder with its prompt filled in, by handing a `claude://code/new` link to *ChatLinks*, the opener *Chat* holds (`Chat.opener`); a page in the app's Browser pane cannot hand the app that link, so the board opens a ticket's chat through it, and `repos.open` opens a new repository's chat through it. A run that names a file in `CDD_OPENED_CHATS` gets *RecordedChatLinks*, which keeps each link in that file instead of opening the app, so no spec opens a chat on this machine.

The MCP tools are `chat.list`, `chat.open`, `chat.send(kind, text)`, `chat.messages`, `chat.remove`, and `chat.resend` for the sender, and `chat.check_in`, `chat.confirm`, and `chat.finish`, which the cdd-board mod calls from inside the chat. The board's TypeScript reaches them through the language adapter the installer deploys.

- **Purpose:** Let the board drive any connected chat — send it a command and follow that command until the chat has shown and finished it — without the chats and the board sharing a process.
- **Seam (terms):** Chat, ChatCommand, ChatMessage, ChatNotConnectedError, ChatLinks, RecordedChatLinks, `chat.list`, `chat.open`, `chat.send`, `chat.messages`, `chat.remove`, `chat.resend`, `chat.check_in`, `chat.confirm`, `chat.finish`
- **Dependencies (one-way):** `harness/agent_tools` (the toolset annotations, and *ChatPointer*, which finds a chat's transcript by its id; the chat finds it once and keeps its path in `chat.json`, so reading its title again does not search the Claude projects folder), `harness/installation`, `harness/mcp`. It imports nothing from space, tools, or cdd_guidance, so it sits in harness above harness/mcp.

## Constraint

Send only to a connected chat; sending to a chat whose mod has not checked in lately raises *ChatNotConnectedError*. Only the chat itself calls `chat.check_in`, `chat.confirm`, and `chat.finish`; a sender uses `chat.send`, `chat.resend`, and `chat.remove`. A fill waits while a turn runs, so do not expect it to show before the turn ends.
