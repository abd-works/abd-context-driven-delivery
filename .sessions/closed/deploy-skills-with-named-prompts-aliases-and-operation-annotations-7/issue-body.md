# Deploy skills with named prompts, aliases, and operation annotations

## Forward requirements (from prompt)

- Better control over deploying skills and actions
- Better naming of deployed skills and commands
- An easier way to put in the actual prompts we want when we need to override
- Possibly aliases
- Annotations on the actual operations for where they should go (skills, commands)
- Some annotations may be for rules as well

## Current deploy (from agent_skills)

- Host-action skills/commands come from hardcoded lists and templates
- Companions come from hardcoded tuples plus a shared template
- Workflow slash names are listed in agent_skills, not declared on the operations
- No per-operation override of SKILL.md or command prompt body
- No aliases
- No annotation on tools/actions for deploy target (skill, command, rule)

## Handoff

# Handoff — agent_skills (2026-08-26)

## Resume

- **Stage:** (unset)
- **Last work:** (see session progress below)
- **Next action:** Deploy skills with named prompts, aliases, and operation annotations
- **Next focus:** Deploy skills with named prompts, aliases, and operation annotations

## Artifacts to read

- `utilities/agent_skills/.context/module-context.md`
- `.context/context-index.md`
