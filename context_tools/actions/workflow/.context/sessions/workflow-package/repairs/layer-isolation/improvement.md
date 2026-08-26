# layer-isolation

- **tool:** bdd
- **error:** Copied workspace git branch policy into workflow sketch — HEAD on session branch, clean/dirty tree checkout/create/refuse, mergeable branch, merge conflicts. Workflow depends on workspace for that; its scope is validate session opened and branch set for the work session after start, plus workflow outcomes (Project status, issue body, trailers, finish orchestration).
- **rule:** layer-isolation
- **how:** Removed workspace git branch/dirty-tree/merge-conflict branches from start and finish. After open work session: it should set the branch to the session branch for that work session. Finish keeps workflow outcomes only (merge orchestration, Project Done, close issue, trailers).
