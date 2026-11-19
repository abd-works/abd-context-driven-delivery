# harness/git
*Git* runs the git command line in one folder, with a time limit that suits the command (10 s for reads; 180 s for commands that reach origin or read or rewrite the whole working tree: push, fetch, pull, checkout, merge, worktree, add, commit) and no inherited stdin (which hangs git under the MCP server on Windows): `Git(folder).run(*args, env=..., timeout=...)` answers git's output, and `succeeds(*args)` answers whether a command such as `show-ref --verify` succeeds. `listed(*args)` answers the entries of a command that lists files, such as `ls-files`, `diff --name-only` or `status --porcelain`, each as git writes it under `-z`, so a name with letters outside ASCII, a quote, a backslash or a tab is the name the file has on disk. Every failure, whether git is missing, times out, or exits with an error, raises *RepoConnectError*. The repository tools (space/repo), the session's file reads (space/session), the catalog's source links, the release and the test cadence (harness/diagnostics), and the pinned cdd runtime (harness/mcp) all run git through it.

- **Purpose:** Run git the same way everywhere, with one set of time limits and one error, so no caller has to stop a hung git or read its exit code.
- **Seam (terms):** Git, RepoConnectError.
- **Dependencies (one-way):** none, so harness/catalog_generator, harness/diagnostics, harness/mcp, space/repo, and space/session all use it without depending on each other.

## Constraint

Run git only through *Git*, so every git command gets the same time limit and the same error. Git for Windows' `cmd\git.exe` is a launcher, so a git that outlives its limit is stopped with its whole process tree; stopping only the launcher leaves the real git holding the output pipes.
