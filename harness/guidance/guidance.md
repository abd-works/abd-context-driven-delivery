## Overview

Show the CDD guidance overview: the practices, their fidelities, and the actions that run on them. Use it to choose which practice and action to run next.

## Where artifacts go

Every artifact belongs to the folder its session works on, not to the repository. A session names that folder, its workpath, when it is created (`harness/kanban`, for example), and every path a fidelity declares is relative to it, because work on one part of a repository should stay beside that part. An artifact sits at the repository root only when the session names no folder.

Artifacts have no separate root folder such as `src` or `tests`: code goes straight in the session's folder. Markdown and drawio always go in that folder's `.context/`, so what explains the code stays apart from the code and agents find it in one place.

Temporary output such as logs and validation reports goes in `.sessions/{session}/`, because it describes one piece of work rather than the code.
