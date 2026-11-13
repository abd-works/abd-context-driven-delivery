# File Viewer And Selection Comments: Research

Research for the stories View Files In Rich Viewer and Add Comment To File Selection in [review-work-in-board-files.md](review-work-in-board-files.md), done 2026-11-12.

**Question:** how does a person select text in a file, write a comment on it, and send it to the chat with the file's name, the lines, and the selected text, the way a design canvas comment reaches Claude? And can the file be opened for editing and saved?

## The comment toolbar you have seen is the claude.ai Artifact comment layer

The toolbar that shows up in some windows and not others belongs to the claude.ai shell that hosts Artifacts and Claude Design canvases. It appears only on a page served from claude.ai, such as an artifact or a design canvas, never on a page served from localhost. That is why it shows up in the browser pane only some of the time. The design canvas comments are this same layer: this repository publishes its canvases to Claude Design (`harness/design_canvas/versions.py` records their `claude.ai/artifact/...` links), and Claude Design draws the comments. No comment code lives in this repository.

A page reaches the layer through the Artifact runtime's `comments` capability (contract 0.2.96, `comments.d.ts`):

- **`openComposer({range})`** opens the shell's own comment composer on a DOM `Range`. The selected text becomes the comment's quoted excerpt. The declaration `{comments: {"composer_only": true}}` grants this verb with no consent prompt.
- **`customAnchors()`** lets the page anchor comments itself, for content the shell cannot anchor to. `compose(anchor, at, {label, detail})` opens the composer on a name the page invents, at most 128 bytes, such as `space/session/file_manager.py:L158-L176`. The `label` is the short line the viewer sees, such as "file_manager.py lines 158–176", and the `detail` holds the selected text. Of the detail, at most 512 bytes are sent to Claude. Page-invented names need the full form `{comments: {"customAnchors": true}}`, which asks the viewer for consent once.
- **Send to Claude**, the button on a thread in the shell, posts the comment and sends it to every Claude session watching the artifact. The comment arrives there as `[Artifact comment sent to Claude]`, together with its anchor and label, and Claude replies in the thread. A page can also send through `sendToClaude({anchor, text})`, but only editors of the artifact can use it, and only from a viewer's own click or key press.
- **The page can read the files live.** Through the `mcp` capability it can call the cdd tools as `host:plugin_cdd_cdd`, so `file-manager.read` works, and a new write operation would work the same way. This works only when the viewer opens the page in the Claude desktop app with cdd connected.

**Claude Docs is built on this layer and goes furthest with it.** A Claude Doc is a claude.ai artifact that Claude edits through the Claude Docs connector. A person selects words in the doc and comments on them. A comment's anchor is the words themselves, its thread holds replies and its resolution, and a suggestion proposes a change to the words for someone to accept. A comment sent to Claude arrives as an `[Artifact comment sent to Claude]` turn that names the thread. Claude reads the thread, makes the change in the doc, and replies under the comment. This is the select, comment, send and reply loop we want, already built. The catch is that a doc holds its own copy of the text, not the repository file. To review a file this way, the file has to be put into a doc, and every accepted change has to be written back to the file on disk. For prose such as a story map, a handoff, or this research, that copy is a fair price for full commenting. For code that Monaco shows and saves, it is not.

**What this means:** the Claude feature can be used, but only by a file view published as a claude.ai Artifact. It cannot be used by the board or by the graph app, which run on localhost.

**Limits:**
- Monaco draws its own selection. It is not a native DOM selection, and Monaco renders only the lines in view, so `openComposer({range})` cannot see a Monaco selection reliably. `customAnchors().compose` with a `path:Lx-Ly` name avoids this, because it does not need a DOM range.
- The selected text sent to Claude is capped at 512 bytes. A longer selection reaches Claude only as its line range, so Claude reads the lines from the file.
- Comments are write-only from the page. The shell draws every thread, and the page must not draw its own list.

## The pipe that reaches a live chat from our own apps: the board's chat queue

Inside the board and the graph app, which run on localhost, the way into a chat is the board's chat queue:

1. The board calls `ticket.chat.fill(ticket.inSession(prompt))`, or `submit`, which posts to `POST /api/chat/:id/send`.
2. That runs the MCP tool `chat.send` (`harness/chat/chat.py:138`), which queues the message for the chat.
3. The cdd-board mod's check-in picks the message up and puts it in the chat's prompt box, or submits it.

The report's Fix button already sends `file:line` and the quoted lines this way (`space/kanban/app/src/kanban/ticket/report-client.ts`). A message is plain text, so the file, the lines, the selection and the comment all go into the prompt itself. No consent prompt is needed, and the 512-byte cap does not apply.

## Existing tools that do this

- **[Plannotator](https://github.com/backnotprop/plannotator)** is an open-source Claude Code plugin with about 9.9k stars. `/plannotator-annotate path/to/file` opens a file in a review page in the browser. There you select text, then delete it, comment on it, or suggest a replacement, and **Send Feedback** returns every annotation to the session. Its Claude Code mod (Claude Code 2.1.287 or later) delivers the feedback as a message from the plugin, so Claude does not wait while you review. That is the same shape as our cdd-board mod and chat queue. It is the closest working example of the interaction we want: select, mark, comment, and send everything at once. It does not edit files in Monaco, and it is a separate app, not part of the board. ([Claude Code docs](https://docs.plannotator.ai/open-source/agents/claude-code))
- **[Agentation](https://github.com/Wahajolla/annotator-skill)**, used through the annotator-skill plugin, adds a click-to-comment toolbar to web pages. Each note carries the element's selector, the text around it, and the page's URL. It comments on elements, not on text in files.
- **[revu](https://awesome.ecosyste.ms/projects/github.com%2Fkud%2Frevu-vscode)** and **[Local Review](https://github.com/dkzlv/local-review)** are VS Code extensions. VS Code is built on Monaco. They put comment threads on a line or a selection, kept in the gutter, and export the review to an AI agent.
- **[crit](https://github.com/tomasz-tomczyk/crit)** is a review tool with inline comments and a send action on each comment. Its agent support is experimental.
- **[Zed](https://git.secluded.site/zed/commit/415f384ff3d4d7bb91f2eee89dede46d1324df0c)** stores diff-review comments locally and sends them all to its agent with one **Send Review to Agent** button.
- **[Velt](https://velt.dev/libraries/monaco)** sells comment threads for Monaco. It is commercial, not open source.

## The file viewer today

- **Graph app** (`harness/graph/app/source/SourceView.tsx`): Monaco through `@monaco-editor/react` 4.7 and `monaco-editor` 0.57, bundled by Vite. It is always read-only. It shows a node's excerpt from `graph.source`, not a whole file, and it highlights only Python and TypeScript.
- **A shared viewer already exists.** `harness/installation/templates/typescript/cdd-files.tsx` is installed as `@cdd/cdd-files`. Its `SourceViewGenerated` reads a file through `file-manager.read` and shows it in read-only Monaco. No application uses it yet.
- **The board** draws files as plain numbered lines, read through `session.read_file`.
- **The file shape** today:
  - `FileText{path, text}` and `Folder{folder, entries: FolderEntry[]}` come from `space/session/file_manager.py`.
  - `FileEntry{path, exists}` comes from the board's file lists.
- **Saving:** no MCP operation writes a file's content. Edit and Save needs one on the file manager, such as `file-manager.write(path, text)`, kept to the workpath's folders as `read` is.
- **Where the code goes:** files resolve from the session's workpath, and `SessionFiles` returns full paths where a tool needs them. The viewer and its typed file shape live in `space/`, beside `file_manager.py`. harness, space and tools may import each other, so the graph app and the board can both import the viewer.

## Recommendation

Build the comment flow on the board's chat queue, and design it after Plannotator and the Artifact comment layer:

1. **Viewer:** one Monaco file view in `space/`, typed on the file manager's `FileText`. It renders by type, as the catalog already does: Monaco for code, rendered HTML for markdown, and draw.io for `.drawio` files (`harness/catalog_generator/catalog_examples.py:149-170`). **Edit** turns Monaco's read-only off, and **Save** calls the new `file-manager.write`.
2. **Selecting and commenting:** when Monaco's selection changes, show a small **Comment** button beside the selection, using a Monaco content widget. The button opens a composer. A comment keeps its anchor as `path:Lstart-Lend`, the same name the Artifact layer would use, plus the selected text.
3. **Sending:** **Send to chat** sends one comment, and **Send all** sends every pending comment at once, as Plannotator and Zed do. The message goes through `ticket.chat.fill`, or `submit`, using the board's queue. The prompt carries, for each comment:
   - the file path from the workpath, and the line range;
   - the selected text in a fenced block with its line numbers;
   - the comment;
   - `session=<session.json>`.

   Lines are marked with `>` the way the report's Fix prompt marks them.
4. **For prose reviewed by people:** put the markdown file into a Claude Doc. Comments, threads, suggestions and Send to Claude then work with nothing built. Accepted changes have to be written back to the file on disk.
5. **Optional, later:** for a review someone else does on claude.ai, publish the same read view as an Artifact. It declares `comments` with `customAnchors`, and `mcp` for `host:plugin_cdd_cdd` so it reads the files live. Its comments then reach the chat through the native Send to Claude button. This is the only way to get the claude.ai toolbar itself, and it works only on claude.ai, inside the desktop app.

To try the interaction before building it, install Plannotator and run `/plannotator-annotate` on one of this ticket's files.

## Sources

- Artifact runtime `comments` capability, contract 0.2.96 (`comments.d.ts`, from the Claude Code artifact-capabilities skill)
- [Claude Code desktop docs](https://code.claude.com/docs/en/desktop.md): the browser pane, and Ctrl+Shift+S to select an element
- The Claude Docs connector's guide, `topic.comments`: comments anchored on words, threads, suggestions, and the `[Artifact comment sent to Claude]` turn
- [Claude Code artifacts docs](https://code.claude.com/docs/en/artifacts.md): artifact comments and Send to Claude
- [Plannotator for Claude Code](https://docs.plannotator.ai/open-source/agents/claude-code), [Plannotator on GitHub](https://github.com/backnotprop/plannotator)
- [annotator-skill (Agentation)](https://github.com/Wahajolla/annotator-skill), [Local Review](https://github.com/dkzlv/local-review), [revu](https://awesome.ecosyste.ms/projects/github.com%2Fkud%2Frevu-vscode), [crit](https://github.com/tomasz-tomczyk/crit), [Zed's Send Review to Agent](https://git.secluded.site/zed/commit/415f384ff3d4d7bb91f2eee89dede46d1324df0c), [Velt for Monaco](https://velt.dev/libraries/monaco)
- In this repository: `harness/chat/chat.py`, `space/kanban/app/src/kanban/ticket/report-client.ts`, `harness/graph/app/source/SourceView.tsx`, `harness/installation/templates/typescript/cdd-files.tsx`, `space/session/file_manager.py`, `harness/catalog_generator/catalog_examples.py`
