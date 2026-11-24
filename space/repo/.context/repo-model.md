# space/repo

A *Repo* is one checkout of the local clone: the main clone or a linked worktree beside it. A *Branch* is a named branch on it and answers where it is checked out; its *Worktrees* are the repository's checkouts, each a *Repo*.

- **Purpose:** Give every caller one object graph for the clone, its branches and worktrees, and its commits, so version control is never reimplemented with raw git output.
- **Seam (terms):** Repo, ServedCheckouts, Branch, Worktrees, Commit, NewRepository, MadeRepository, WorktreeNotRemovedError, WorktreeFolderTakenError, MergeRefusedError
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/git, harness/hooks, harness/mcp, space/work_state

## Repo

One checkout of a git repository: its branches and its commits, what its git holds asked of its *Checkout*. The checkouts beside it are its `worktrees`.

+ Repo(root: str | Path = '.')
------
+ root: Path
+ << composition >> checkout: Checkout
+ default_branch: Branch
+ << composition >> git: Git
+ << composition >> worktrees: Worktrees
+ << composition >> publishing: Publishing
+ << composition >> refs: Refs
+ << composition >> working_tree: WorkingTree
+ << composition >> origin: Origin
+ << composition >> merges: Merges
+ is_clone: bool
+ is_linked_worktree: bool
+ is_main_clone: bool
+ checkout_folder: Path
+ branches: list[Branch]
	-> GitFacts.branch_names
+ current_branch: Branch
	-> GitFacts.head_branch
+ is_on_branch: bool
+ current_commit: str
+ has_origin: bool
+ default_start_point: str
+ << association >> main_clone: Repo
----
+ of_project(project: Path): Repo
	-> Checkout.holding
	-> ServedCheckouts.at
+ path_from_top(path: Path | str): str
+ branch_named(name: str): Branch
+ catch_up_with_origin(fetched: bool = False): None
	// a checkout that cannot reach origin stays as it is, and the log says why
+ close(commit_message: str): Branch
	// a linked worktree: its branch saved, its folder removed
	-> Branch.save
	-> Worktrees.remove
+ push_commit(message: str, untracked: bool = True, sync_remote: bool = True): Commit
	-> Publishing.push_commit
+ push_work(): Commit
	-> Publishing.push_work
+ merge_to_main(): Commit
+ push_to_main(): Commit
+ make_repository(): str
	-> NewRepository.make_from_folder
+ push(hint: str = ''): str
---<<creates>>--> Branch
---<<creates>>--> Commit
---<<creates>>--> Worktrees
---<<runs>>--> Git
---<<raises>>--> RepoConnectError
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> ToolSubject
---<<annotated with>>--> Mcp
---<<annotated with>>--> LongCall
---<<annotated with>>--> Command

## ServedCheckouts

The repository of every checkout this process works in, each made once and held while it runs, so every tool call and every session of one checkout work on the same Repo.

+ ServedCheckouts()
------
----
+ at(root: Path): Repo
+ serve(repo: Repo): Repo
---<<creates>>--> Repo

## Commit

One git commit: its sha, subject, full message, and the trailers the message carries, which is what an MCP tool that makes a commit answers with.

+ Commit(sha: str, message: str)
------
+ sha: str
+ subject: str
+ message: str
+ trailers: dict[str, str]
----

## Branch

Named branch on a *Repo*: where it is checked out, and checking it out, saving it, merging it, and deleting it.

+ Branch(repo: Repo, name: str)
------
+ repo: Repo
+ name: str
+ exists: bool
+ is_checked_out: bool
	// any checkout of the repository has it
+ is_checked_out_here: bool
	// the checkout it was found from has it
+ is_default: bool
+ << association >> checkout: Repo | None
	-> Worktrees.of
+ << association >> linked_worktree: Repo | None
	// the checkout that has it when that is a linked worktree, not the main clone
+ start_point: str
----
+ changed_files(): list[str]
	// read through Git.listed, so a file whose name git would quote is listed by the name it has on disk
+ check_out(): Branch
+ open_in_worktree(): Repo
	-> Worktrees.open
+ save(commit_message: str, push: bool = True): None
	// the one "commit everything in the checkout that has it, and push it when origin lacks some of it"
+ push(): None
	// push its commits from the checkout that has it when origin lacks some of them, committing nothing
+ land_on_default(): None
+ merge_into_default(): Repo
+ delete(unmerged: bool = False): None
---<<asks whether a ref exists through>>--> Repo
---<<finds its checkout through>>--> Worktrees

## Worktrees

The checkouts of one repository, as `git worktree` lists them: the main clone and each linked worktree, each the *Repo* this process holds for its folder. Which branch each has out is read from the listing, so no git starts for each checkout.

+ Worktrees(repo: Repo, checkouts: ServedCheckouts)
------
+ by_branch: dict[Branch, Repo]
----
+ repository_at(folder: Path | str): Repo
+ at(folder: Path | str): Repo | None
+ of(branch: Branch): Repo | None
+ open(branch: Branch): Repo
	-> Repo.catch_up_with_origin
+ primary_root(): Path
	-> Checkout.main_folder
+ sibling_folder(branch: Branch): Path
+ add(path: str | Path, branch: Branch): Repo
	// a folder already at path that is not the branch's checkout raises WorktreeFolderTakenError, unless it is the empty folder a removed worktree left
+ remove(worktree: Repo): None
	// stops the checkout's hook daemon first; a folder still there afterwards raises WorktreeNotRemovedError
---<<lists>>--> Repo
---<<reads the listing through>>--> GitFacts
---<<stops>>--> HookDaemon
---<<raises>>--> WorktreeNotRemovedError
---<<raises>>--> WorktreeFolderTakenError

## NewRepository

A folder made a git repository of its own on main, its .gitignore given what CDD writes into a project.

+ NewRepository(repo: Repo)
------
+ root: Path
----
+ create(): MadeRepository
+ make_from_folder(): MadeRepository
+ ignore_as_cdd_does(): int
+ write_ignores(): int

## MadeRepository

What making a folder a repository did; the tool that made it words it.

------
+ root: Path
+ was_there: bool
+ branch: str
+ ignored_lines: int
+ sentence: str
----

## WorktreeNotRemovedError : RuntimeError

A worktree's folder still there after git, a forced delete, and the Windows fallbacks each tried to remove it; it names the folder left behind.

+ WorktreeNotRemovedError(folder: Path)
------
+ folder: Path
----

## WorktreeFolderTakenError : RuntimeError

A branch is to be opened in a worktree whose folder is already there and is not that branch's checkout; it names the branch and the folder.

+ WorktreeFolderTakenError(branch: str, folder: Path)
------
+ branch: str
+ folder: Path
----

## MergeRefusedError : RepoConnectError

Git refused to merge one branch into the branch a checkout has checked out, such as when both changed the same lines. The merge is undone before this is raised, so the checkout is as it was.

+ MergeRefusedError(branch: str, into: str, refusal: str)
------
+ branch: str
+ into: str
+ refusal: str
----
