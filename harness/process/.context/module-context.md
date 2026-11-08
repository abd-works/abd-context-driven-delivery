# harness/process
*BackgroundStart* starts a server that keeps running after the chat that started it, with no console window on Windows (`run(command, cwd=..., env=..., log=...)`, or its `creationflags` and `startupinfo` for a caller that starts the process itself); `inside_starters_job()` is the same start for a Windows job that refuses to let its children leave. *PythonInterpreter* is the Python to start: `windowless` for a background server, `console` for a hook command whose JSON the IDE reads from stdout.
*RunningProcess* is a process on this computer by its id, asked whether it is still running; the hook server's lock file, *HookDaemon*, *McpDaemon*, and `scripts/instances.py` name processes this way. *StoppableProcess* is a running process this code may stop, and it waits for the process to exit, or raises *ProcessNotStopped*.
The process classes live in one module, `process.py`, since each is a few lines about one process on this computer.
*Git* runs the git command line in one folder, with a time limit that suits the command and no inherited stdin (which hangs git under the MCP server on Windows); every failure raises *RepoConnectError*. The repository tools (space/repo), the catalog's source links, and the pinned cdd runtime all run git through it.

- **Purpose:** Start, name, and stop the processes the framework keeps, and run git, the same way on Windows and elsewhere.
- **Seam (terms):** BackgroundStart, PythonInterpreter, ExclusivePort, RunningProcess, StoppableProcess, ProcessNotStopped, Git, RepoConnectError. The module is a toolkit, not one deep class: each class is a small tool for one job on this computer that its callers use directly, so every class is part of the seam by design, and a deep-module count that reads all of them as exposed reads the toolkit's purpose. A class added here is one more such tool, never a helper of another class here.
- **Dependencies (one-way):** none, so harness/hooks, harness/mcp, harness/catalog_generator, space/repo, and the scripts all use it without depending on each other.

## Constraint

Start a background server with *BackgroundStart* and `PythonInterpreter().windowless`, and a hook command with `PythonInterpreter().console`: `pythonw.exe` drops stdout. Run git only through *Git*, so every git command gets the same time limit and the same error.
