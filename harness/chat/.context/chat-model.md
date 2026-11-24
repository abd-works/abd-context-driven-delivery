# harness/chat

*Chat* is a Claude Code chat reached from outside it, so the session board can see which chats are connected and send one a command; *ChatCommand* is a command a chat takes at its check-in, and *ChatMessage* is a command as the board lists it.

- **Purpose:** Let the board drive any connected chat — send it a command and follow that command until the chat has shown and finished it — without the chats and the board sharing a process.
- **Seam (terms):** Chats, Chat, ChatCommand, ChatMessage, ChatNotConnectedError; the MCP operations `chats.list`, `chats.open`, `chat.send`, `chat.messages`, `chat.remove`, `chat.resend`, `chat.check_in`, `chat.confirm`, `chat.finish`
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/mcp

## Chats

The Claude Code chats on this machine: the ones connected now, and a new one opened in the Claude app through the opener the chats hold.

+ Chats(folder: Path, opener: ChatOpener, asking: str = "")
------
----
+ load(call: ToolCall | None = None): Chats
+ new_chat(folder: str, prompt: str): NewChat
+ list(): list[Chat]
+ open(folder: str, prompt: str): str
---<<lists>>--> Chat
---<<annotated with>>--> LanguageAdapter

## Chat

Reach a Claude Code chat from outside it and send it a command. A chat is a folder every process can read: the chat alone writes its state when it checks in, and a sender adds one file per command to its waiting folder.

+ Chat(folder: Path)
------
+ id: str
+ name: str
+ is_busy: bool
+ folder: str
+ is_connected: bool
----
+ load(chat: str): Chat
+ send(kind: CommandKind, text: str): Chat
+ messages(): list[ChatMessage]
+ check_in(is_busy: bool = False, name: str = '', folder: str = ''): list[ChatCommand]
+ confirm(message: str, is_shown: bool, reason: str = ''): Chat
+ finish(message: str): Chat
+ resend(message: str): Chat
+ remove(message: str): Chat
---<<loads>>--> ChatPointer
---<<reads and writes its state with>>--> JsonFile
---<<creates>>--> ChatCommand
---<<creates>>--> ChatMessage
---<<raises>>--> ChatNotConnectedError
---<<annotated with>>--> LanguageAdapter

## ChatCommand

A command a chat takes at its check-in: the message it came in, and what to do with its text.

+ ChatCommand(message: str, kind: str, text: str)
------
+ message: str
+ kind: str
+ text: str
----

## ChatMessage : ChatCommand

A message sent to a chat, as the board lists it: when it was sent, where it stands, and why it failed.

+ ChatMessage(message: str, kind: str, text: str, sent_at: float, state: MessageState, reason: str)
------
+ sent_at: float
+ state: MessageState
+ reason: str
----

## ChatNotConnectedError : LookupError

Raised when a command is sent to a chat whose mod has not checked in lately.

+ ChatNotConnectedError(chat: str)
------
----
