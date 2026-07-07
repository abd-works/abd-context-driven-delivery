# cdd-capability

Define, discover, and deploy CDD capabilities.

read in full → `.cdd/cdd-capability/cdd-capability.md`

## Create
Create a new capability folder with the required surfaces and config.
read `@cdd-capability` §Create

## Identify
Check whether a folder is a valid CDD capability.
read `@cdd-capability` §Identify

## Discover
Find all CDD capabilities under a root directory.
read `@cdd-capability` §Discover

## Deploy
Copy the capability to the IDE deployment area, generate a `SKILL.md` wrapper, and write one command file per `##` section.
read `@cdd-capability` §Deploy

## Inject
Declare that this capability inherits commands from another capability. Updates `.cdd-config.json` with an `injected` entry; the next `deploy` generates the merged SKILL.md and command files.
read `@cdd-capability` §Inject

## Clean
Remove all deployed artefacts using the target recorded in `.cdd-config.json`.
read `@cdd-capability` §Clean

## Validate
read `@rules` §Validate
