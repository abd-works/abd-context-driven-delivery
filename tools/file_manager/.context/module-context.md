# tools/file_manager
*FileManager* lists and reads the files under the current session's roots — the folder each of its practices works in — so every application shows files the same way instead of each object growing a read operation of its own. `FileManager.current()` is the file manager of the session being worked on; `session.file_manager` is the same object.

*Folder* is a listed folder and its entries, folders first; *FolderEntry* is one entry with its path and size. *FileEntry* is a declared file with its path from the project and whether it exists. *FileText* is a file's path and its text.

The MCP tools are `file-manager.list(folder)` and `file-manager.read(path)`; the board's TypeScript reaches them through the language adapter the installer deploys.

- **Purpose:** Give every caller one safe way to list and read a session's files, confined to the folders that session works in.
- **Seam (terms):** FileManager, Folder, FolderEntry, FileEntry, FileText, PathOutsideRootsError, `file-manager.list`, `file-manager.read`
- **Dependencies (one-way):** `harness/agent_tools`, `harness/installation`, `harness/mcp`, `space/session` (`FileManager.current`). `space/session`, `space/repo`, and `space/kanban` import this module, and `space/session` is imported back — a cycle tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Name paths from the session's workpath. A path outside the session's roots raises *PathOutsideRootsError*, so a caller cannot read the rest of the disk through a session. `read` returns no text for a file that is gone, such as one deleted since a page listed it; check `FileText.text` rather than expecting an error.
