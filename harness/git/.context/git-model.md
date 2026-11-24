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
+ listed(*args: str): list[str]
	// the entries of a command that lists files, each as git writes it under -z: never quoted and never trimmed, so a name with letters outside ASCII, a quote or a tab is the name the file has on disk
+ succeeds(*args: str): bool
---<<raises>>--> RepoConnectError

## RepoConnectError : RuntimeError

Raised when git cannot be run, or a git command fails, in a clone.

------
----

## Checkout

One checkout of a repository, known by its top folder: whether it is the main clone or a linked worktree, the branch it has out, and the facts its git holds. The framework (harness/mcp, harness/process, harness/agent_tools) and space/repo's *Repo* each ask one, so git's facts have one reader on both sides of the boundary.

+ Checkout(folder: Path | str)
------
+ folder: Path
+ is_clone: bool
+ is_main: bool
+ is_linked_worktree: bool
+ main_folder: Path
+ branch: str
	// empty for a checkout on no branch or a folder that is no clone
+ << association >> facts: GitFacts
	// GitFolder once its .git files can be read; AskedOfGit for refs only git reads; NoGitFacts for a folder that is no clone; chosen again until the files can be read
----
+ holding(folder: Path | str): Checkout
	// the nearest folder at or above folder that git marks as a checkout's top, else folder itself

## GitFacts

<< interface >> What a checkout's git holds, each answered as git itself answers it.

------
----
+ head_branch(): str
+ is_on_branch(): bool
+ head_commit(): str
+ has_ref(ref: str): bool
+ branch_names(): list[str]
+ has_remote(name: str): bool
+ worktrees(): list[tuple[Path, str]]
+ common_folder(): Path
+ is_merging(): bool
	// a merge going on in this checkout, found in a linked worktree's own git folder as in the main clone's .git

## GitFolder : GitFacts

A checkout's facts read from the files of its .git, so a lookup asked many times in one board read starts no git.

+ GitFolder(checkout: Path)
------
+ checkout: Path
+ is_readable: bool
----
+ main_checkout(): Path
+ commit_of(ref: str): str

## AskedOfGit : GitFacts

A checkout's facts asked of the git command line, for refs only git reads, such as a reftable.

+ AskedOfGit(git: Git)
------
----
---<<runs>>--> Git

## NoGitFacts : GitFacts

The facts of a folder that is no clone: nothing, never asking git, which would fail or find a repository above it.

+ NoGitFacts(folder: Path)
------
----
