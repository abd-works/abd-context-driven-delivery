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

## Story: Run Fidelity Action With Overlays

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
