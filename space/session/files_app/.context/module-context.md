# space/session/files_app

The *Files app* shows a session's files beside the chat and takes a person's comments on them back to that chat: the file viewer as an app of its own, on its own server and port (`app/ports.json`, 8783), which reads only the files its link names and never the board. It is the one place a session's files are viewed; the chat bar's files button, its session name, and an `open_file` another page sends a chat all open it. Stories and scenarios: the main map's (E) Review Generated Work In File Viewer (`harness/.context/stories/story-map.md`, `harness/.context/stories/review-generated-work-in-file-viewer/`); acceptance tests: `review-files-in-files-app.story.*.py`, `app/files/*.spec.ts`. Model: `.context/files-app-model.md`.

**Opening it.** Python registers it once as an *App* (`files_app.py`, `FILES_APP`, harness/diagnostics); a chat readies it with `app.open('Files')` and starts its server while it is not running. A link names what to show and who opened it:

| Query | Means |
|---|---|
| `files=<ticket>&fidelity=<slug,slug>` | the files of those fidelities of the ticket; the chat bar's files button names every fidelity of the shown stage, every practice's |
| `session-folder=<ticket>` | every file in `.sessions/<ticket>` |
| `file=<path>` | the file to open first; a `.drawio` file is not opened on load, only on a click |
| `chat=<id>` | the chat that opened the page, which its comments and practice changes are sent to |
| `project=<folder>` | the project every call names (`X-CDD-Project`) |

**What it calls.** Its server (`app/files-server.ts`) answers only this machine's own page and serves the generated routes of `session.*`, `file-comments.*`, `fidelity-progress.*`, `practice-session-output.*`, and one chat route, `chat.send`, through the cdd server; so the Files app does what those operations do and holds no rule of its own. The page reads the session's practices with `session.show`, and a practice toggle calls `practice-session-output.enable` then sends the chat a `refresh`, which its chat bar answers by reading the board again. A comment is added, edited, sent and cleared with the `file-comments.*` tools; the open file is read with `session.file` (text, comments, folds, violations), again every two seconds while a comment on it is sent. A `.drawio` file opens the draw.io editor (`tools/drawio_viewer`, port 8791) in a tab opened during the click, started first when nothing answers its port.

**Callers must honour.** A link names its files; one with neither `files` nor `session-folder` shows that it names none. A practice change reaches the chat bar only while the chat checks in with the board, as comments do. A field added to a session operation's data reaches the page only after the language adapters are written again (an install, or `Installer.write_language_adapters`) and the app is built again.

**Depends on:** the generated TypeScript adapters (`.claude/language-adapters/typescript`), the graph explorer's source view (`harness/graph/app/source`), harness/diagnostics (*App*, *AppServer*), and the cdd server. Nothing imports it.
