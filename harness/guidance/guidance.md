## Overview

Show the CDD guidance overview: the practices, their fidelities, and the actions that run on them. Use it to choose which practice and action to run next.

## Where artifacts go

Every artifact belongs to the folder its session works on, not to the repository. A session names that folder, its workpath, when it is created (`space/kanban`, for example), and every path a fidelity declares is relative to it, because work on one part of a repository should stay beside that part. An artifact sits at the repository root only when the session names no folder.

Artifacts have no separate root folder such as `src` or `tests`: code goes straight in the session's folder. Markdown and drawio always go in that folder's `.context/`, so what explains the code stays apart from the code and agents find it in one place.

A session's `session.json` can name a root folder for a practice, under its workpath, and that root takes the place of the session's folder for that practice: with workpath `a/b/c` and `d` as the Stories root, the story map goes in `a/b/c/d/.context/story-map.md` and the Stories code in `a/b/c/d/{epic}/{sub-epic}/…`. Every practice works this way, because one rule tells every agent where to look. A root is a folder for code, never a `.context` folder, because the practice's documents already go in its root's `.context/`; choosing one is refused, since it would put code among the documents and nest a `.context` inside a `.context`.

Temporary output such as logs and validation reports goes in `.sessions/{session}/`, because it describes one piece of work rather than the code.
