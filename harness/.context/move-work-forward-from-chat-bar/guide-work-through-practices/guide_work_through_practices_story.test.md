---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Guide Work Through Practices

### Domain terms

- ++files pane++ — the pane the chat bar opens beside the chat, as the Session Board opens its files panel, holding a fidelity's files or its validation report.
- ++action button++ — the band's ▶ chip and its ▾ action list, which run an action on the fidelity the band shows.

## Story: View Fidelity Files

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: the Files button read story-map.md and story-map.drawio into the chat, over a 96,711 character session.read_file answer; files open in a window of their own, as the board's do |
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/view-fidelity-files/view_fidelity_files_story.test.ts` | the story test that plays these scenarios |

#### Scenario: Open the files beside the chat, never in it

*Given* checkout-flow's clean-engineering-model declares chat-bar-model.md and chat-bar-model.drawio  
*When* the Person opens the files of clean-engineering-model  
*Then* the files pane opens beside the chat, titled clean-engineering-model files  
  *And* the chat bar above the prompt draws no file tab  
  *And* the diagram is never read as text

## Story: Read Validation Report From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: opening stories-scenarios-20261107T001054.md showed it inside the chat interface; it opens in the side panel |

#### Scenario: Read the violations from their count

*Given* checkout-flow's clean-engineering-model has 7 violations in its latest validation report  
*When* the Person presses the count 7  
*Then* the report opens in its own tab of the side panel  
  *And* its text is drawn as markdown there, not in the chat

## Story: Invoke Next Fidelity Action

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: every action the chat bar sends must include the session param and the format param; with the story map picked, ▶ and its ▾ action list left the band |
| `harness/guidance_actions/guidance_actions.py` | every guidance action reads a `format=` word and a `session=` word from its guidance |

#### Scenario: Run the next action on the selected fidelity

*Given* checkout-flow's ux-mockup is generated and is the selected fidelity  
*When* the Person runs the next action  
*Then* /actions-validate ux-mockup in markdown, in checkout-flow's session, waits in the prompt box for the Person to send

#### Scenario: Keep the action button on a done fidelity

*Given* checkout-flow's stories-scenarios is done and is the selected fidelity  
*When* the Chat Bar draws checkout-flow  
*Then* the button still shows, offering the stage's first action, generate stories-scenarios  
  *And* its ▾ still opens the action list
