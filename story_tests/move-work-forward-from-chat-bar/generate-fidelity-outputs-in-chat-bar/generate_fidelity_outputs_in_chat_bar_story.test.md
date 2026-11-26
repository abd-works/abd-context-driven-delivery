---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Generate Fidelity Outputs In Chat Bar

### Domain terms

- ++overlay++ — a pattern the session has chosen on the chat bar; its graph applies it, and Generate follows its shared rules.
- ++overlays word++ — the `overlays=` word a command names the overlays in, comma separated, beside its `format=` word.

> In steps: ++example++ names a row of a table below.

## Examples

### overlays

| overlay | shared rules open with |
| --- | --- |
| ++lern_domain_driven++ | Whenever you create, alter, or delete a LERN domain module under `src/` |
| ++mern_domain_driven++ | Whenever you create, alter, or delete a domain-module feature package |

## Story: Apply Chosen Overlays To Fidelity Action

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-11 | "doesnt result in LERN being passed in as a param? shouldnt it?", on `/actions-generate stories-acceptance-tests clean-engineering-code session=... format=python` with LN chosen |
| `harness/chat-ui/pane/hooks/chat-bar/action-button-view.tsx` | `pressAction` adds the format chips' `format=` word to the command |
| `cdd_guidance/patterns/lern_domain_driven/lern_domain_driven.md` | its `## Shared rules` section |

#### Scenario: Name the chosen overlays in the command

*Given* checkout-flow's session overlays ++lern_domain_driven++
*When* the Person runs generate on stories-acceptance-tests from the chat bar
*Then* the prompt holds the generate command for stories-acceptance-tests
  *And* the command ends with overlays=lern_domain_driven

Evidence still missing: the chat bar's TypeScript story tests were removed in commit 8c56ab052, so this scenario is checked by eye on the live chat bar.

#### Scenario: Choose the overlays a command names

*Given* checkout-flow's session overlays none
*When* Claude Code generates stories-acceptance-tests with overlays=lern_domain_driven
*Then* checkout-flow's session overlays lern_domain_driven

#### Scenario: Follow each overlay's shared rules when generating

*Given* checkout-flow's session overlays ++lern_domain_driven++ and ++mern_domain_driven++
*When* Claude Code generates stories-acceptance-tests
*Then* the instructions name each overlay as a pattern overlay
  *And* they hold each overlay's shared rules

#### Scenario: Generate with no overlay chosen

*Given* checkout-flow's session overlays none
*When* Claude Code generates stories-acceptance-tests
*Then* the instructions name no pattern overlay

#### Scenario: Judge each overlay's shared rules when validating

*Given* checkout-flow's session overlays ++lern_domain_driven++ and ++mern_domain_driven++
*When* Claude Code validates stories-acceptance-tests
*Then* the report names each overlay as a pattern overlay
  *And* it holds each overlay's shared rules

#### Scenario: Validate with no overlay chosen

*Given* checkout-flow's session overlays none
*When* Claude Code validates stories-acceptance-tests
*Then* the report names no pattern overlay

## Story: Choose Format

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/hooks/chat-bar/guidance-client.ts` | a format chip's press calls `session.toggle_guidance` with part format and the chip's group, such as markdown |
| `space/session/practices/guidance_selection.py` `GuidanceSelection.toggle` | the press selects the format group beside those selected, or no longer, saved in session.json |
| `.sessions/ui-fixes-as-i-use-it/exploratory-testing/defects/pip-1-two-format-toggles-at-once-lose-one.md` | Reported 2026-11-26: two presses on different chips at the same moment kept only one |

#### Scenario: Keep two format presses made at the same moment

*Given* checkout-flow's session works on Stories in Discovery, with the markdown chip chosen and the diagram chip not  
*When* the Person presses the markdown chip on the chat bar while another chat presses the diagram chip on the same session  
*Then* checkout-flow's format chips show diagram chosen and markdown not  
  *And* the guidance selection's version is raised once for each press

#### Scenario: Refuse a format press no chip stands for

*Given* checkout-flow's session works on Stories in Discovery, whose chips are diagram and markdown  
*When* Claude Code presses the format drawio on checkout-flow's guidance selection  
*Then* the press is refused, naming drawio and the chips diagram and markdown  
  *But* checkout-flow's guidance selection and its version are not changed

Intended (pip-2, 2026-11-26): as `ticket.choose_formats` refuses a label no chip has; a stage pressed by its title (Discovery) or a practice by any name but its key (Stories) is refused the same way.

#### Scenario: Refuse a format press that would leave a fidelity no format

*Given* checkout-flow's session works on Stories in Discovery, with markdown the only format chosen for the story map  
*When* the Person presses the markdown chip off on the chat bar  
*Then* the press is refused, saying markdown is the only format chosen for the story map  
  *But* the story map keeps markdown chosen, and the markdown chip stays chosen

Intended (pip-4, 2026-11-26): as `FidelitySessionOutput.choose_format` refuses leaving out a fidelity's last format (*LastFormatLeftOut*), so a fidelity writes in at least one format whichever control the person presses.
