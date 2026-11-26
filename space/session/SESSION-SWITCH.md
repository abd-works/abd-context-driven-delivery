# What a chat is told when it switches to a session

Each section below is one note `sessions.switch` may open its answer with, filled in with the names of the switch it
answers. The notes come before the log's own instructions, in this file's order, and only the ones that apply are said.

## Worktree ticket

This chat works in {ticket}'s own worktree, so its session is {ticket}, not {asked}. To work on {asked}, open it from the main chat.

## Outside worktree

This chat works in {chat}, but {session}'s worktree is {worktree}. Do this session's work in a chat started there (start_session with cwd {worktree}), not in this chat.

## Default roots

**Output roots.** These practices write under their default folders, which nobody has checked: {roots}. Before generating anything, set up the session's roots with session.set_up_roots, so they cover exactly the pieces the ticket works on in every practice. A practice's documents and its code or tests can sit in different areas, each where the practice's declared outputs place them, and the pieces of one ticket are spread across them: a domain folder, the package that implements it, the story tests that cover it. Propose the roots from what the ticket names and what its branch changed (fidelity-session-output.propose_roots answers the folders each fidelity proposes), dig down to the most local folder that holds each piece rather than a parent that also holds its siblings, and confirm them with the person before setting any. Then set them: practice-session-output.choose_root for the practice's own root, fidelity-session-output.choose_root for a fidelity kept apart, and fidelity-session-output.add_root for each further folder beside it, so the Files app, the board and validate show this ticket's files and new work lands beside them. Leave a default that already holds them, or where none exist yet.
