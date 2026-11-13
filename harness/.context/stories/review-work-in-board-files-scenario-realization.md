---
fidelity: [specification]
artifact: [scenario-realizations]
format: md
section: body
---

# Scenario Realizations: Review Work In Board Files

Source:
- `move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/review_files_in_viewer_story.test.md`
- `move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md` (Open Session Files From Details, and the changed-files filter of List Ticket Files)

Each page call reaches one MCP tool, which calls one domain operation (cdd_web_domain_access). The new pieces are `FileManager.write`, `FileText.language`, `FileComments`, `FileComment`, and `FileCommentState`. The rest exist today.

A file comment's state is read, not stored twice. It is `not_sent` until `Chat.send` returns, then `sent`, then `processed` once its chat message is done: the chat's turn that worked on it has ended (`harness/chat/chat.py:279-286`).

---

## List Ticket Files

### Scenario: Filter the list to the files the ticket's branch changed

**When** the Person filters the list to changed files only

```realization
FidelityProgress.files(ticket, fidelity)
<- [FileEntry{path, exists, is_changed}]
filesPanel.showChangedOnly(true)  the page filters the entries it already holds on is_changed
```

**Then** only src/mine_spec.py is listed.

---

## Open Session Files From Details

### Scenario: Open the session folder from the session button

```realization
sessionButton.open(ticket)  only for a ticket's own session, not main and not expanded
  -> files.openSessionFolder(ticket)
    -> Session.folder_files()
    <- [FileEntry] under .sessions/checkout-flow
```

### Scenario: Open the latest handoff from the details

```realization
page.files.openSessionFile(ticket, ticket.session.handoff)
  -> Session.read_file(".sessions/checkout-flow/handoff-20261110.md")
  <- FileText{path, text}
```

### Scenario: Open the workpath folder from the details

```realization
page.files.openWorkpathFolder(ticket)
  -> FileManager.list("")
  <- Folder{folder: "harness/.context", entries}
```

### Scenario: Say there is no handoff yet

```realization
ticket.session.handoff
  -> Session.latest_handoff
  <- ""
```

---

## View Files In Rich Viewer

### Scenario: Show a code file in the viewer with its lines numbered

```realization
FileView(file: "src/checkout/order.py")
  -> SessionAdapter.read_file("src/checkout/order.py")
    -> Session.read_file("src/checkout/order.py")
    <- FileText{path, text, language: "python"}
```

### Scenario: Render a markdown file as the page it describes

```realization
Session.read_file("src/checkout/README.md")
<- FileText{path, text, language: "markdown"}
FileView renders markdown as HTML
```

---

## Save Edited File

### Scenario: Save the edited text to the file on disk

```realization
FileView.save()
  -> SessionAdapter.write_file("src/checkout/order.py", text)
    -> Session.write_file("src/checkout/order.py", text)
      -> SessionFiles.write(path, text)
        -> FileManager.write(path, text)  refuses a path outside the roots
    <- FileText{path, text, language}
```

---

## Add Comment To File Selection

### Scenario: Mark a comment beside the selection's first line

```realization
FileCommentsAdapter.add("src/checkout/order.py", 12, 14, selected_text, "an empty cart should say which cart and why")
  -> FileComments.add(path, start_line, end_line, selected_text, text)
    -> FileComment(path, start_line, end_line, selected_text, text)
    -> FileComments._save()  .sessions/checkout-flow/file-comments.json
  <- FileComment{anchor: "src/checkout/order.py:L12-L14", state: not_sent}
```

### Scenario: Open a file comment from its marker

```realization
FileComments.on("src/checkout/order.py")
<- [FileComment{anchor, text, state}]
```

### Scenario: Delete a file comment

```realization
FileComments.remove("src/checkout/order.py:L12-L14")
  -> FileComments._save()
<- FileComments
```

### Scenario: Keep file comments when the page reloads

```realization
FileComments.load(call)
  -> Session.file_comments  read from .sessions/checkout-flow/file-comments.json
FileComments.on("src/checkout/order.py")
<- [FileComment]
```

---

## Send File Comments To Chat

### Scenario: Add a comment to the chat's queue

```realization
FileComments.send("src/checkout/order.py:L12-L14", "checkout-chat")
  -> FileComment.prompt
     "src/checkout/order.py:12-14: <comment>" then the lines marked "> 12 | ..."
  -> Chat.load("checkout-chat").queue("fill", prompt + "

session=.sessions/checkout-flow/session.json")
  <- ChatMessage{message}
  -> FileComment.sent_in(chat, message)
  -> FileComments._save()
<- FileComment{state: sent}
```

### Scenario: Send every open comment at once

```realization
FileComments.send_open("checkout-chat")
  -> FileComments.open  the comments whose state is not_sent
  -> Chat.load("checkout-chat").queue("fill", one prompt joining each comment's prompt)
  <- ChatMessage{message}
  -> FileComment.sent_in(chat, message)  for each open comment
  -> FileComments._save()
<- FileComments
```

### Scenario: Keep the comment unsent when the chat is not connected

```realization
FileComments.send("src/checkout/order.py:L12-L14", "checkout-chat")
  -> Chat.load("checkout-chat").queue("fill", prompt)
  <- ChatNotConnectedError("chat 'checkout-chat' is not connected: is the cdd-board mod loaded in it?")
```

The comment is marked sent only after `Chat.send` returns, so it stays not_sent.

---

## Mark File Comment Processed

### Scenario: Mark a comment processed once the chat has worked on it

```realization
Chat.check_in(is_busy=False)
  -> Chat._finish_worked_on(False)  moves the shown message to done
FileComments.on("src/checkout/order.py")
  -> FileComment.state
    -> Chat.load("checkout-chat").message(message)
    <- ChatMessage{message, state: done}
  <- processed
```

### Scenario: Keep a comment sent while the chat still works on it

```realization
FileComment.state
  -> Chat.load("checkout-chat").message(message)
  <- ChatMessage{message, state: shown}
<- sent
```

---

## Show Changed File In Viewer

### Scenario: Show the agent's change to the open file

```realization
FileView sees FileComment{anchor: "src/checkout/order.py:L12-L14"} turn processed
  -> Session.read_file("src/checkout/order.py")
  <- FileText{text with the agent's line 14}
```

---

## Clear Processed File Comments

### Scenario: Clear the processed comments, keeping the rest

```realization
FileComments.clear_processed()
  -> FileComments._save()  keeps the comments that are not_sent or sent
<- FileComments
```
