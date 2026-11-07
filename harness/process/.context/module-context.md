# harness/process
*RunningProcess* is a process on this computer by its id, asked whether it is still running; the hook server's lock file, *HookDaemon*, *McpDaemon*, and `scripts/instances.py` name processes this way. *StoppableProcess* is a running process this code may stop, and it waits for the process to exit. The process helpers start Python in the background with no console window on Windows (`windowless_python_executable`, `detached_creationflags`, `hidden_process_startupinfo`), or on a console whose output a caller reads (`console_python_executable`).

- **Purpose:** Name, start, and stop the long-running processes the framework keeps, the same way on Windows and elsewhere.
- **Seam (terms):** RunningProcess, StoppableProcess, ProcessNotStopped; `windowless_python_executable`, `console_python_executable`, `detached_creationflags`, `hidden_process_startupinfo`
- **Dependencies (one-way):** none, so harness/hooks, harness/mcp, and the scripts all use it without depending on each other.

## Constraint

Start a background server with `windowless_python_executable` and `detached_creationflags`, and a hook command, whose JSON the IDE reads from stdout, with `console_python_executable`: `pythonw.exe` drops stdout.
