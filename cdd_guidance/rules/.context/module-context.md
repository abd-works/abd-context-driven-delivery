# cdd_guidance/rules
*Rules* are the always-on rules the installer puts into every IDE: coding conventions (`coding.mdc`), writing guidelines, how to locate context, learning from corrections (with its `corrections.log`), failing loudly on MCP errors, test timing, worktree ownership and the draw.io viewer. They hold no code.

- **Purpose:** State, once, the rules every agent follows in every chat, whatever practice it works in.
- **Seam (terms):** each rule by its file name
- **Dependencies (one-way):** none; installed by `harness/installation`.

## Constraint

A rule applies everywhere; a rule that belongs to one practice or fidelity goes in that practice's markdown instead. Change the rule here and reinstall; never edit an installed copy.
