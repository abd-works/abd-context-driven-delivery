# space/session/files

The files a session works with, as its pages list, read, show, and comment on them; the session's core makes these and mixes *SessionExplorer* into *Session*.

- **Purpose:** List, read, save, show, and comment on the files a session works with, without letting a call reach a file outside the session's roots.
- **Seam (terms):** SessionFiles, FileManager, FileEntry, FileText, PathOutsideRootsError, SessionFile, FileTooLongToShowError, FileComments, SessionExplorer
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/mcp, harness/chat, harness/graph, harness/markdown, harness/git

## SessionExplorer

Mixed into *Session*: the published graph tools a page browsing the session's files calls, each reading the session's graph itself.

----
+ graph_trees(paths: list[str], call: ToolCall | None = None): list[ExplorerEntry]
	-> SessionPaths.in_project
	-> Graph.load_files
	-> Graph.explorer_trees
+ graph_branch(node_id: str, paths: list[str]): ExplorerEntry | None
	-> Graph.explorer_branch
+ graph_node_ranges(node_id: str, paths: list[str]): list[Range]
	-> NodeSpans.collect
+ graph_members(): list[NodeSource]
	-> Graph.source_members

## FileManager

List and read the files under a session's roots, the folders its practices work in, named from its workpath. Moved here from tools/file_manager.

+ FileManager(workpath: Path | str, roots: tuple[Path, ...])
------
+ workpath: Path
+ roots: tuple[Path, ...]
----
+ load(call: ToolCall): FileManager
	-> ToolCall.session
+ list(folder: str = ''): Folder
+ read(path: str): FileText
	// never reads a path outside the session's roots; such a path raises PathOutsideRootsError, and one inside a .git folder VersionControlPathRefused
+ write(path: str, text: str, version: str = ''): FileText
	// a file on disk that is no longer the version its read answered raises FileChangedSinceReadError and is left as it is
+ find(pattern: str): list[Path]
---<<creates>>--> Folder
---<<creates>>--> FileText
---<<raises>>--> PathOutsideRootsError
---<<raises>>--> VersionControlPathRefused
---<<raises>>--> FileChangedSinceReadError
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> NoSessionLog

## FileEntry

One file something declares, such as a fidelity's output, as a path from the project, and whether it is there yet.

+ FileEntry(path: str, exists: bool)
------
+ path: str
+ exists: bool
----

## FileText

The text of one file, with its path from the workpath; no text for a file that is not there, which `exists` tells from a file that is there and empty.

+ FileText(path: str, text: str, version: str, exists: bool = True)
------
+ path: Annotated[str, SourceFile]
+ text: str
+ version: str
+ exists: bool
----

## VersionControlPathRefused : PermissionError

A read or write aimed inside a repository's .git folder, which holds git's own record: a hook written there runs on the person's next commit.

+ VersionControlPathRefused(path: str)
------
+ path: str
----

## FileChangedSinceReadError : RuntimeError

A write of a file that is no longer the version its caller read: changed, made or deleted on disk since, so saving would lose that change unseen.

+ FileChangedSinceReadError(path: str, version: str, on_disk: str)
------
+ path: str
+ version: str
+ on_disk: str
----

## PathOutsideRootsError : ValueError

A path outside every root of the session, which a page may name but never reach.

+ PathOutsideRootsError(path: str)
------
----

## FileTooLongToShowError : ValueError

The viewer asked for a file longer than it shows, `VIEWER_SHOWS_LINES` (30,000) lines: drawing it would freeze the page.

+ FileTooLongToShowError(path: str, lines: int, shown: int = VIEWER_SHOWS_LINES)
------
+ path: str
+ lines: int
+ shown: int
----
