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
