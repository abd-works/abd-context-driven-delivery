# ContextConfig stays in the installation module, beside the other JSON files CDD keeps in a project

The round-5, round-6 and round-7 reviews (harness core, row 10 in round 7) pointed out that the installer never reads *ContextConfig*, a project's `.context/config.json`, and asked for it to move to the module that owns the project's `.context/`, or for a record that keeps it.

*ContextConfig* stays in `harness/installation`.

## Why

- **Its readers sit on both sides of the framework, so it has to stay low.** The hook server reads a guideline to turn a pattern's hooks on (`harness/hooks`), a session reads where each practice writes (`space/session`), and the Granola tools read the `.context` folder's name (`tools/granola`). `harness/` may import nothing from `space/` or `tools/`, so the class must live in harness at or below `harness/hooks`. The modules there are annotations, markdown, agent_tools and installation; of these only installation owns files CDD keeps in a project.
- **It is one of the JSON files installation already owns.** Round 7 gave the JSON object files one owner, *JsonFile* (`harness/installation/json_file.py`): `.context/config.json`, an install's `diagnostics.json`, its `.install-state.json`, and the hook files read and write through it, each with its own kind of *JsonFileUnreadable*. Moving *ContextConfig* elsewhere would split that job across modules again.
- **No module owns "the project's `.context/`" as a whole.** Decision records live in `space/session`, the context index in `cdd_guidance/context_setup`, Granola notes in `tools/granola`. A new module for one small class would add a dependency for every reader without giving the folder an owner.

## Consequences

- `CONTEXT_FOLDER` stays the one name of the `.context` folder, read from `harness.installation.context_config`.
- The installation card names *ContextConfig* and *JsonFile* as part of its seam.
