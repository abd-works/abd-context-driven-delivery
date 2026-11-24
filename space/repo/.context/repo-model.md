# space/repo

A *Repo* is the local clone; a *Branch* is a named branch on it, its *Worktrees* are its checkouts, and a *Worktree* is one of them.

- **Purpose:** Give every caller one object graph for the clone, its branches and worktrees, and its commits, so version control is never reimplemented with raw git output.
- **Seam (terms):** Repo, ServedCheckouts, Branch, Worktrees, Worktree, Commit, WorktreeNotRemovedError
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/git, harness/hooks, harness/mcp, space/work_state

## Repo

Local git clone: its branches and its commits. The checkouts beside it are its `worktrees`.

+ Repo(root: str | Path = '.')
------
+ root: Path
+ default_branch: str
+ << composition >> git: Git
+ << composition >> worktrees: Worktrees
+ << composition >> publishing: Publishing
+ << composition >> refs: Refs
+ << composition >> working_tree: WorkingTree
+ is_clone: bool
+ is_linked_worktree: bool
+ checkout_folder: Path
+ branches: list[Branch]
+ current_branch: Branch
+ current_commit: str
+ default_start_point: str
+ << association >> main_clone: Repo
+ own_work_state: WorkState
+ work_state: WorkState
+ open_worktree: Worktree | None
----
+ of_project(project: Path): Repo
	-> ServedCheckouts.at
+ primary_root(): Path
+ path_from_top(path: Path | str): str
+ branch_named(name: str): Branch
+ push_upstream(): None
+ needs_push(): bool
+ fetch(): None
+ pull(): None
+ merge_from(other: Branch, message: str = ''): str
+ switch_branch(name: str = ''): str
	-> Branch.switch_to
+ close_branch(name: str = '', commit_message: str = 'branch: close'): str
	-> Branch.close
	-> LatestRelease.keep
+ switch_worktree(name: str = ''): str
	-> Branch.move_to_worktree
+ close_worktree(commit_message: str = 'worktree: close'): str
	-> Worktree.close
+ switch_branch_command(): str
+ close_branch_command(): str
+ switch_worktree_command(): str
+ close_worktree_command(): str
+ push_commit(message: str, untracked: bool = True, sync_remote: bool = True): Commit
	-> Publishing.push_commit
+ push(hint: str = ''): str
---<<creates>>--> Branch
---<<creates>>--> Commit
---<<creates>>--> Worktrees
---<<creates>>--> LatestRelease
---<<runs>>--> Git
---<<calls succeeds on>>--> Git
---<<raises>>--> RepoConnectError
---<<creates>>--> WorkState
---<<reads the answering call from>>--> ToolCall
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

Named branch on a *Repo* — checkout, commit, merge, and close.

+ Branch(repo: Repo, name: str)
------
+ repo: Repo
+ name: str
+ exists: bool
+ is_checked_out: bool
+ is_default: bool
+ << association >> worktree: Worktree | None
+ start_point: str
----
+ changed_files(): list[str]
+ check_out(): Branch
+ switch_to(): Branch
+ open_in_worktree(): Worktree
	-> Worktrees.open
+ move_to_worktree(): Worktree
+ save(commit_message: str): None
+ land_on_default(): None
+ delete(unmerged: bool = False): None
+ close(commit_message: str = 'branch: close'): None
---<<asks whether a ref exists through>>--> Repo
---<<finds its checkout through>>--> Worktrees

## Worktrees

The checkouts of one repository, as `git worktree` lists them: the main clone and each linked worktree, each with the branch checked out there.

+ Worktrees(repo: Repo)
------
----
+ repository_at(folder: Path): Repo
+ at(folder: Path | str): Worktree | None
+ of(branch: Branch): Worktree | None
+ open(branch: Branch): Worktree
+ sibling_folder(branch: Branch): Path
+ add(path: str | Path, branch: Branch): Worktree
+ remove(worktree: Worktree): None
	// stops the checkout's hook daemon first; a folder still there afterwards raises WorktreeNotRemovedError
---<<lists>>--> Worktree
---<<stops>>--> HookDaemon
---<<raises>>--> WorktreeNotRemovedError

## Worktree

One checkout of the repository, as the *Worktrees* that listed it found it: its folder, its own *Repo*, and the branch checked out there, each made once when it is listed.

+ Worktree(worktrees: Worktrees, path: Path | str, branch_name: str)
------
+ path: Path
+ << association >> repository: Repo
+ << association >> branch: Branch | None
+ sync_failure: str
----
+ fetch_pull(): None
+ close(commit_message: str): Branch
	-> Branch.save
	-> Worktrees.remove
---<<calls branch_named on>>--> Repo

## WorktreeNotRemovedError : RuntimeError

A worktree's folder still there after git, a forced delete, and the Windows fallbacks each tried to remove it; it names the folder left behind.

+ WorktreeNotRemovedError(folder: Path)
------
+ folder: Path
----
