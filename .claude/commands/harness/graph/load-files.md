Build each practice from only the given files and run its rules on them.

``files`` are files or folders, relative to ``folder`` or absolute; a folder
stands for the source files under it. Use it for the files being edited:
it reads them as they are now and never touches the saved graph.

Use MCP tool: `graph.load_files(folder: 'str', practices: 'list[str]', files: 'list[str]', overlays: 'list[str] | None' = None)`
