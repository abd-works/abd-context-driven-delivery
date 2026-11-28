# cog-03 (question) Turning the last practice off makes the selection, and every action command, cover all five practices, while the board calls the stage done

**Title** - With Stories, DDD and UX on and Clean Engineering and BDD off, turning Stories, DDD and UX off leaves no practice selected; the selection then lists the fidelities of all five practices, the generate command runs on all five (CE and BDD included) with `format=python`, and the board marks the ticket done in Discovery with the story map not started.

**Charter** - theme 7. **Tester** - Cog.

**Story** - Choose Session Practices (chat bar) and Choose Ticket Practices / "Finish a stage on the practices left on" (board). No scenario covers turning every practice off.

**Module and class** - `space/session/practices/guidance_selection.py` *GuidanceSelection._of_practices_in* (`[... if output.enabled] or self._outputs`) and `commands_on`; the board's `Ticket.is_done` (space/kanban) for the done flag.

**Severity** - question (it may be meant: the docstring of `fidelities` says "no practice selected every practice"). If it is not meant, it is a wrong result: one press of Generate on the chat bar works on two practices the person had switched off.

## Steps

Sandbox and server as in cog-01. Session `.sessions/checkout-flow/session.json`, Clean Engineering and BDD off, Stories, DDD and UX on, Discovery the only stage.

1. `session.toggle_guidance` practice `stories`, then `ddd`, then `ux`.
2. `session.guidance_selection` and read `fidelities`, `formats` and `commands.generate`.
3. `board.show`, read checkout-flow's `is_done` and progress.

## Expected

Either the last practice cannot be turned off, or no practice on means no fidelity is shown or acted on; in neither case does Generate reach Clean Engineering and BDD, which were off before and after. A stage with no practice on is not "done".

## Actual

```
practices [('stories', False), ('ddd', False), ('ux', False), ('clean_engineering', False), ('bdd', False)]
fidelities ['stories-story-map', 'ddd-bounded-context', 'ux-ia', 'clean-engineering-modules', 'bdd-behavior']
formats [('diagram', False), ('markdown', False), ('code', True)]
generate: /actions-generate stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior session=.sessions/checkout-flow/session.json format=python
board: column Discovery, is_done True; stories-story-map enabled=False state=not_started
```

The `format=python` comes from the code group (BDD behavior's), which is chosen, so the story map, bounded-context map and IA would be asked for in Python too.

## Tier that should catch it

Unit (`session_spec.py` checks turning Stories off alone, `expect(... if practice.is_selected).to(equal([]))`, but not what fidelities and commands then hold).
