# harness/process

*BackgroundStart* and *PythonInterpreter* start a server without a console window, *RunningProcess* asks about and ends one by its id, *ExclusivePort* is the one port a server may hold, *CappedLogFile* keeps a log a server or the session writes under a size, so it cannot fill the disk, *LockFile* is a file the operating system locks for one holder at a time, and *ServerDaemon* is the one model of a long-running server that the hook daemon and the cdd server both are.

- **Purpose:** Start, name, and stop the processes the framework keeps, the same way on Windows and elsewhere.
- **Seam (terms):** BackgroundStart, Wmi, OutsideJobStartFailed, PythonInterpreter, ExclusivePort, RunningProcess, ProcessNotStopped, StarterBoundJob, JobNotMade, CappedLogFile, LockFile, LockFileHeld, ServerDaemon, RunningServer, ServerDidNotStart
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
+ started_at: datetime | None
	// when the process started, as the operating system keeps it; the system gives an ended process's id to a later one, so the id together with this time names one process
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

## StarterBoundJob

The processes a starter holds to its own life: each process it takes in, and every process those start, is ended by Windows when the starter ends, however it ends, so no child goes on working in a folder the next starter believes is free. Outside Windows it holds nothing.

+ StarterBoundJob()
------
----
+ take_in(process: subprocess.Popen): None
---<<raises>>--> JobNotMade

## JobNotMade : Exception

Windows refused the job object, or refused to put a process in it.

+ JobNotMade(step: str, pid: int = 0)
------
+ step: str
+ pid: int
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
+ last_lines(count: int): str

## LockFile

A file the operating system locks for the one holder that claimed it, naming that holder's process at its start: the install lock of an IDE folder, the lock beside a JSON file several processes change, and the start lock of a server. The operating system gives the lock back when its holder's process ends, however it ends.

+ LockFile(path: Path, wait_seconds: float)
------
+ path: Path
+ wait_seconds: float
+ is_held: bool
+ holder: int
----
+ held(): Iterator[None]
+ claim(): None
	// waits while another holder has the file, then refuses; one holder may claim again, and the file is free once its first claim is given back
+ release(): None
---<<raises>>--> LockFileHeld

## LockFileHeld : TimeoutError

Another holder kept a lock file for longer than a claim waits for it.

+ LockFileHeld(path: Path, holder: int, waited_seconds: float)
------
+ path: Path
+ holder: int
+ waited_seconds: float
----
+ message(): str

## ServerDaemon

A server that keeps running past the command that started it, on the one port it may hold, with its output in a capped log file: the hook daemon of a checkout and the one cdd server. One start at a time, through a start lock beside the log.

+ ServerDaemon(port: ExclusivePort, log: CappedLogFile)          abstract
------
+ port: int
+ << composition >> log: CappedLogFile
----
+ running(): RunningServer | None          abstract
+ is_running(): bool
+ ensure(): RunningServer
	// starts the server when none answers and waits until it answers, else raises ServerDidNotStart with the log's last lines
+ stop(): None
	// stops the process that answers, else the one holding the port
+ restart(): RunningServer
+ spawn(): RunningProcess
---<<starts with>>--> BackgroundStart
---<<one start at a time through>>--> LockFile
---<<raises>>--> ServerDidNotStart

## RunningServer

A long-running server that answered when asked: its process, the folder it serves code from, the stamp of the code it loaded, and the projects its chats have worked on.

+ RunningServer(process: RunningProcess, serves: Path | None = None, code: str = "", projects: tuple[str, ...] = ())
------
+ << composition >> process: RunningProcess
+ pid: int
+ serves: Path | None
+ code: str
+ projects: tuple[str, ...]
----
+ is_serving(folder: Path): bool

## ServerDidNotStart : Exception

A server was started but did not answer within its wait.

+ ServerDidNotStart(daemon: ServerDaemon, seconds: float, log_tail: str)
------
+ daemon: ServerDaemon
----

## ServedAnswers

The answers the process gives from one checkout's sessions (`answer_reads.py`): none until *CallSessions* begins one.

+ ServedAnswers()
------
+ current: int | None
----
+ begin(): None

## LogTimestamp

The time a session log line, a hook log entry, or a toast is stamped with: a moment in UTC, to the second, such as `2026-11-07T17:30:05Z`, so every log's lines sort and compare alike.

+ LogTimestamp(moment: datetime)
------
+ moment: datetime
----
+ now(): LogTimestamp
+ read(text: str): LogTimestamp
