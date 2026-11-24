# harness/process

*BackgroundStart* and *PythonInterpreter* start a server without a console window, *RunningProcess* asks about and ends one by its id, *ExclusivePort* is the one port a server may hold, and *CappedLogFile* keeps a log a server or the session writes under a size, so it cannot fill the disk.

- **Purpose:** Start, name, and stop the processes the framework keeps, the same way on Windows and elsewhere.
- **Seam (terms):** BackgroundStart, Wmi, OutsideJobStartFailed, PythonInterpreter, ExclusivePort, RunningProcess, ProcessNotStopped, CappedLogFile
- **Dependencies (one-way):** *(none)*

## BackgroundStart

How a background server is started so it keeps running without a console window, past the chat that started it: it breaks away from the starter's job, or, where the job refuses, WMI creates it outside every job.

+ BackgroundStart(log: IO[str] | None = None, wmi: Wmi | None = None)
------
+ log: IO[str] | None
+ creationflags: int
+ startupinfo: subprocess.STARTUPINFO | None
----
+ run(command: list[str], cwd: str | Path, env: dict[str, str]): RunningProcess

## Wmi

Windows Management Instrumentation through PowerShell: Win32_Process.Create makes a process outside every job of the caller's.

+ Wmi()
----
+ create(command_line: str, folder: str, env: dict[str, str]): int

## RunningProcess

A process by its id, to ask whether it is still running and which ports it listens on, and to end it, such as the server an address file names.

+ RunningProcess(pid: int)
------
+ pid: int
+ alive: bool
+ listening_ports: list[int]
----
+ stop(wait_seconds: float): None
	// never signals an id of 0 or this process's own id, so a blank or stale address file cannot end the process that reads it
---<<raises>>--> ProcessNotStopped

## ProcessNotStopped : Exception

A process was asked to stop and is still running.

+ ProcessNotStopped(pid: int, cause: BaseException | None = None)
------
+ pid: int
+ cause: BaseException | None
----

## ExclusivePort

The one port a long-running server of this computer may listen on, claimed by an exclusive bind: two servers cannot both hold one port, and no lock file can promise that once its holder is killed without cleanup.

+ ExclusivePort(host: str, port: int)
------
+ host: str
+ port: int
----
+ claim(): socket.socket | None
+ holder(): RunningProcess | None
---<<names its holder as>>--> RunningProcess

## PythonInterpreter

One Python on this computer.

+ PythonInterpreter(executable: str | Path | None = None)
------
+ executable: Path
+ windowless: str
+ console: str
----

## CappedLogFile

A log file that, once it reaches its size (4 MB), moves its lines to the previous file beside it (`server.log.1`), replacing an older one, so the next line starts a new file. The session log, the hook server's log, and the cdd server's output each keep one.

+ CappedLogFile(path: Path, limit_bytes: int = LOG_SIZE_LIMIT_BYTES)
------
+ path: Path
+ limit_bytes: int
+ previous: Path
+ is_full: bool
----
+ roll_when_full(): bool
	// a log another process holds open cannot be moved on Windows, so it rolls at the next write or start that finds it free
