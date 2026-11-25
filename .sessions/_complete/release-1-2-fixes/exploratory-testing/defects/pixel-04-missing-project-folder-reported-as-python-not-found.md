# A Files page opened on a project folder that is not there says the cdd server is not connected because python.exe was not found

- **Charter:** Round 1 - explore the Files app and the board's pages in a real browser as a person whose files change under the page
- **Tester:** Pixel
- **Story:** Review Generated Work In File Viewer > Open Files In Files App (opened on another project). No scenario covers a project folder that is gone, such as a ticket's worktree removed while its Files tab stays open.
- **Module and class:** `@cdd/cdd-connection` `CddConnection` / `ProjectConnections.of` (used by `harness/files_app/app/files-server.ts`): it starts `connect.py` with the project as the working folder, and Node reports a working folder that is not there as `spawn <program> ENOENT`, naming the program.
- **Severity:** misleading message (it sends the person to repair Python or the cdd server, both of which are fine)

## Steps

Sandbox Files server on 8902 over a cdd server on 8901 that answers every other page (`C:\dev\_et\pixel\work\scripts\stack.py`); script `C:\dev\_et\pixel\work\scripts\t5.py`, case `no-project`.

1. Open `http://127.0.0.1:8902/?files=pixel-files&fidelity=clean-engineering-code&project=C:\dev\_et\pixel\work\nowhere`, where `nowhere` does not exist.

## Expected

The page says the project folder `C:\dev\_et\pixel\work\nowhere` is not there. A session that is not there is said plainly on the same page: "SessionNotFoundError: no session at '.sessions/no-such-session/session.json': name the session.json of the session to work on".

## Actual

Every call answers 500 and the page shows, three times over:

```
The Files app did not read where the session works: The cdd server is not connected: C:\dev\_et\pixel\cdd_home\connect.py failed: spawn C:\Users\jeffa\AppData\Local\Programs\Python\Python312\python.exe ENOENT
```

`python.exe` is at that path and the cdd server is running; the same server answers the page on `repo` a second later. Screenshot: `C:\dev\_et\pixel\work\shots\t5-no-project.png`.

## Tier that should catch it

heavy (a spec of `CddConnection` on a project folder that does not exist): the message comes from a real process start, which a stubbed connection never makes.

## Also seen by

## Confirmation (Rivet, round 2)
- Result: confirmed
- What I ran and saw: my own stack (`pstack2.py`), the page opened with `project=C:\dev\_et\rivet\confirm\nowhere`: 17 responses, all 500, and the page reads "The files did not list: The cdd server is not connected: C:\dev\_et\rivet\confirm\homeF\connect.py failed: spawn C:\Users\jeffa\AppData\Local\Programs\Python\Python312\python.exe ENOENT". The same server listed the files of the real project a moment before. My line starts "The files did not list", the report's "The Files app did not read where the session works": the same failure met by another call.
- Cause, if you found it: as the report says, the connection starts `connect.py` with the project as its working folder; I did not read `@cdd/cdd-connection` further.
- Shares its cause with: rivet's note on a missing checkout (`python -m harness.diagnostics.test_runs heavy <folder that is not there>` ends in a raw `NotADirectoryError [WinError 267]` from the same kind of process start); bolt-09 (a missing folder answered with a raw error).
