# A project keeps its own patterns

A project such as pml-web needs a pattern that goes against a pattern CDD ships: its domain objects save themselves, with no `{Root}Repository` classes, where `lern_domain_driven` and the DDD practice put creation, loading, and search on a repository. CDD only found patterns inside `cdd_guidance/patterns/`, registered once per process in `REGISTERED_PATTERNS`, so a project could neither switch the shipped pattern off nor add its own.

So a project's `.context/config.json` names a folder of its own with `guidelines_folder`, whose subfolders are patterns laid out as a shipped one is (`<name>/<name>.py` defining the class whose `pattern` is `name`, `<name>.md`, `practices/`, `templates/`), and `guidelines` marks each pattern `enabled` or `disabled`. *ProjectGuidelines* (`harness/installation/project_guidelines.py`) reads both for one project: the patterns it works with are the shipped ones and its own, its own replacing a shipped one of the same name, less each it disables. Every reader that lists, applies, chooses, or installs patterns asks the project's guidelines rather than the process's registry: a session's graph (`Graph.use_patterns_of`, which a worker build is told about through its order), the overlays a session may choose and the ticket's overlay choices, the installer's toolsets for the project it installs into, and the cdd server's toolsets for each project it answers (`ProjectToolsets.for_project`, which also gives each project's chat its own tool list).

A project's folder is imported as a package of its own, named from a digest of the folder's path (`cdd_project_guidelines_<digest>`), so two projects the same server answers never share a module, and a pattern's graph rules are imported from `practices/<practice>/rules` by package name as a shipped pattern's are. A project pattern installs under `patterns/`, beside the shipped ones.

A pattern's rules replace a practice's rules of the same name: its graph rules through `checks_of`, as before, and now its written shared rules too, since the practice's text of a rule a pattern the work is held to names again is left out of what generate, render, satisfy, diagnose, and validate hand the agent (`SessionBrief.replaced_rules`). A pattern that drops a practice's rule writes a rule of that name saying what holds instead, such as `repository-is-crud` saying there is no repository.

## Considered options

- **Register a project's patterns in `REGISTERED_PATTERNS` when the project is first served.** Rejected: the registry is one per process, and the cdd server answers several projects, so one project's pattern would be offered to, and applied in, every other.
- **Copy the project's pattern into `cdd_guidance/patterns/`.** Rejected: the pattern belongs to the project and changes with it, and a pattern that contradicts a shipped one would be offered to every project CDD serves.
- **A separate list of practice rules a pattern turns off.** Rejected: a rule of the same name already replaces a practice's graph rule, and a replacing rule says what holds instead, which a bare list of names does not.

## Consequences

- The checkout the cdd server serves from still answers its own calls with every toolset it defines; only another project's server chooses among its guidelines.
- A project's config that disables a shipped pattern now leaves that pattern out of an install into that project, including CDD's own (`mern_domain_driven` is disabled there).
