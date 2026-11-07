# tools/chat
*Chat* is a Claude Code chat reached from outside it, so the session board can see which chats are connected and send one a command. A chat is connected while its cdd-board mod checks in every second; `Chat.load(chat)` is the chat with that id, and `chat.list` lists the connected ones with their name, whether a turn is running, and the folder they work in.

*ChatCommand* is a command a chat takes at its check-in: submit a prompt, fill the prompt box, or run a slash command. *ChatMessage* is a command as the board lists it — when it was sent and where it stands (waiting, taken, shown, done, or failed, with the reason it failed).

The MCP tools are `chat.list`, `chat.send(kind, text)`, `chat.messages`, `chat.remove`, and `chat.resend` for the sender, and `chat.check_in`, `chat.confirm`, and `chat.finish`, which the cdd-board mod calls from inside the chat. The board's TypeScript reaches them through the language adapter the installer deploys.

- **Purpose:** Let the board drive any connected chat — send it a command and follow that command until the chat has shown and finished it — without the chats and the board sharing a process.
- **Seam (terms):** Chat, ChatCommand, ChatMessage, ChatNotConnectedError, `chat.list`, `chat.send`, `chat.messages`, `chat.remove`, `chat.resend`, `chat.check_in`, `chat.confirm`, `chat.finish`
- **Dependencies (one-way):** `harness/agent_tools`, `harness/installation`, `harness/mcp`, `harness/agent_tools` (*ChatPointer*, which finds a chat's transcript by its id)

## Constraint

Send only to a connected chat; sending to a chat whose mod has not checked in lately raises *ChatNotConnectedError*. Only the chat itself calls `chat.check_in`, `chat.confirm`, and `chat.finish`; a sender uses `chat.send`, `chat.resend`, and `chat.remove`. A fill waits while a turn runs, so do not expect it to show before the turn ends.
