# harness/git

*Git* runs every git command in one folder with the same time limits and errors.

- **Purpose:** Run git the same way everywhere, with one set of time limits and one error.
- **Seam (terms):** Git, RepoConnectError
- **Dependencies (one-way):** *(none)*

## Git

The git command line, run in one folder.

+ Git(folder: Path | str)
------
+ folder: Path
----
+ run(*args: str, env: dict[str, str] | None = None, timeout: float | None = None): str
	// every repository operation goes through run, so the time limit, the stop of a hung git, and the RepoConnectError a failure raises are the same for all of them
+ succeeds(*args: str): bool
---<<raises>>--> RepoConnectError

## RepoConnectError : RuntimeError

Raised when git cannot be run, or a git command fails, in a clone.

------
----
