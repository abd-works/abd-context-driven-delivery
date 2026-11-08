# A declared file under a session's root is a value of that root

The round-6 review (harness core, row 10) flagged `FidelitySessionOutput` in `space/session/practice_session_output.py` for making a `DeclaredFile` on each call, and asked that the session output ask `fidelity.declares(path)` instead.

The session output already asks the fidelity whether a found file is one it declares (`_found` calls `fidelity.declares(file, label)`), so matching has one owner: the fidelity, which holds a `DeclaredFile` for each name its outputs declare, made once (`FidelityGuidance._declared_files`).

What the session output still makes is a `DeclaredFile` of a declared name joined to the session's root, to answer two questions about that path: the glob a file search reads (`glob`) and whether it names one plain path (`names_one_path`). That object is kept as a value, made from the path when it is asked, as a `Path` is.

## Why it is not held

- **The root moves while the session lives.** A person chooses a practice's root (`choose_root`), goes back to the default (`use_default_root`), and the session's workpath moves with its worktree. Each move changes every joined path, so a held object would answer for a root that is no longer the session's.
- **The chosen file names replace declared ones.** `output_paths()` puts a single-file output's chosen name in place of the declared one, so the joined paths are not the fidelity's declared names and cannot be the fidelity's held objects.
- **It holds no collaborator.** A `DeclaredFile` is a string and the regular expression made from it, built lazily; making one is the same work as making a `Path`, and nothing reads or writes a file through it.

## Considered options

- **Hold one `DeclaredFile` per joined path in the session output.** Rejected: it is a cache keyed by the root, which goes stale on every move and needs its own clearing.
- **Have the fidelity answer `glob` and `names_one_path` for a path under a root.** Rejected: it hands the root into the fidelity on every call, a parameter the fidelity cannot hold, since one practice's fidelities serve every root its sessions choose.

## Consequences

- `DeclaredFile` stays public in `harness/guidance`, since `space/session` makes these values.
- Matching a found file against a declared pattern stays on `FidelityGuidance.declares`, its one owner.
