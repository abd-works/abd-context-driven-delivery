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
