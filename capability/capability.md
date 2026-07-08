Define, discover, and deploy CDD capabilities.

## Create

Create a new capability folder with the required surfaces and config.

read in full → `template/{capability}/{capability}.md`

Validate the new capability against all rules before committing:

read in full → `../enforce/.cdd/rules/rules.md` §Validate — target: the new capability folder, rule: `cdd-capability/rules/`

## Identify

Check whether a folder is a valid CDD capability.

read in full → `cdd-capability.py` §Capability.is_valid

## Discover

Find all CDD capabilities under a root directory.

read in full → `cdd-capability.py` §list_capabilities

## Deploy

Copy the capability to the IDE deployment area, generate a `SKILL.md` wrapper, and write one command file per `##` section.

Ask the user which IDE and workspace root using `AskQuestion`, then run:

```
python cdd-capability/__main__.py deploy <cursor|vscode> <target-root>
```

- cursor → `.cursor/skills/{capability}/` and `.cursor/commands/{capability}-{command}.md`
- vscode → `.github/skills/{capability}/` and `.github/prompts/{capability}-{command}.prompt.md`

read in full → `cdd-capability.py` §CapabilityDeployer.deploy §DeployTarget §DeployRecord

## Inject

Declare that this capability inherits commands from another capability. Updates `.cdd-config.json` with an `injected` entry; the next `deploy` generates the merged SKILL.md and command files.

```
python cdd-capability/__main__.py --capability <target> inject <source-path> [--commands deploy,clean]
```

- `--commands` omitted → injects all commands the source declares as `injectable`
- Command collision (same slug in own + injected) → own file gets `also read @{source} §{command}` appended

read in full → `cdd-capability.py` §_cmd_inject §InjectedEntry

## Clean

Remove all deployed artefacts using the target recorded in `.cdd-config.json`.

```
python cdd-capability/__main__.py clean
```

read in full → `cdd-capability.py` §CapabilityDeployer.clean

---

## Structure

```
{capability}/
  .cdd-config.json       ← identifies this as a CDD capability; holds deploy state
  {capability}.md        ← agentic surface
  {capability}.py        ← API surface (or .ts, .js, …)
```

A capability may contain sub-capabilities — each sub-folder with its own `.cdd-config.json` is independent.

Example: `enforce` contains `scanners` and `rules`, each a capability in its own right.
