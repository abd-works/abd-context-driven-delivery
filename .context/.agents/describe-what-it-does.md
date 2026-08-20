# Describe what it does

## Rule

When specifying behavior — in agentic surfaces, specs, comments, or docs — state what something **does**: the action, the class, the CLI route, the artifact produced.

After removing wrong logic, delete the false description and write the true one. Replace absence-annotations (“does not…”, “no longer…”, “never…”, “must not…”) with the positive behavior.

## Examples

**Wrong (documents absence):**

- Deploy does not parse `##` sections.
- Generate and Satisfy have no CLI.
- `{Surface}Cli` must not contain business logic.

**Right (documents behavior):**

- Deploy copies the folder to `.cdd/` and writes a SKILL.md pointer to the full `{surface}.md`.
- Generate and Satisfy are agent actions: the agent reads the `##` prose and acts.
- `{Surface}Cli` routes each documented `python -m …` subcommand to the matching `{Surface}` method.
