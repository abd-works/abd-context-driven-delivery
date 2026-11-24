---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Build Prompt Queue

The person puts work on the chat's prompt queue and shapes it before it runs. The queue is kept by the cdd server (`tools/prompt_queue/prompt_queue.py`); the prompt-queue mod (`tools/prompt_queue/hooks/queue/prompt-queue.ts`, `queue-view.tsx`) draws what the server answers. Evidence: the mod's plugin tests (`tools/prompt_queue/hooks/register.test.tsx`), the server's specs (`tools/prompt_queue/prompt_queue_spec.py`, `prompt_queue_heavy_spec.py`) and the story test of Attach Images To Queued Prompt, unless a scenario says otherwise.

### Domain terms

- ++prompt queue++ — the prompts one chat has queued, in order, kept by the cdd server in that chat's own folder.
- ++queued prompt++ — one prompt on the queue, drawn as a card: its id, its text, and whether it is done.
- ++draft++ — the text in the chat's prompt box, not yet sent.
- ++goal++ — a queued prompt seen as the goal its tasks, the steps under it, work towards.
- ++queue archive++ — the folder that keeps a JSON copy of every prompt clear, remove or flush took off, and of the whole queue file each time it was flushed: the session's `queue-archive` folder, or beside the chat's queue file when the chat works in no session.
- ++attachment++ — an image or document pasted in a queued draft, kept as a file beside its prompt.
- ++failure line++ — CDD's one failure line above the chat bar, with its Fix and ✕, which shows the queue's latest failure.

> In steps: ++example++ names an example in a table below.

## Examples

### queued prompts

| queued prompt | id | done |
| --- | --- | --- |
| ++Write the scenarios++ | a | no |
| ++Run the unit tier++ | b | no |

### drafts

| draft | how the person queues it |
| --- | --- |
| ++Run the heavy tier++ | as it is, with Alt+Enter |
| ++also run the heavy tier++ | placed into the plan, with + or /queue |
| ++Write the scenarios again++ | as the changed text of a prompt being edited |

### where the model places a draft

| placed draft | place |
| --- | --- |
| ++Run the heavy tier too++ | a task of ++Run the unit tier++ (b) |
| ++Run the heavy tier card++ | a card of its own, Run the heavy tier |

### pasted list

| pasted list | lines |
| --- | --- |
| ++outstanding items++ | 2. Right-click Go to file on a fold-out. / 3. Files e2e not re-run since the connector fold-outs. / Session roots setup / 7. No story tests for the three Choose Session And Practice Roots scenarios. |

### attachments

| attachment | file |
| --- | --- |
| ++screenshot.png++ | a one-pixel PNG pasted in the draft of ++Write the scenarios++ |
| ++a-1.png++ | C:/chats/chat-1/attachments/a-1.png, kept beside ++Write the scenarios++ |

### what the model answers

| model answer | lists |
| --- | --- |
| ++Nothing is left to do++ | no prompt |

### missing prompt

| prompt | id |
| --- | --- |
| ++missing prompt++ | z, an id the queue does not hold |

### callers changing the queue at once

| caller | process | change |
| --- | --- | --- |
| ++stable lane caller++ | the stable lane's cdd server | queues ++Run the heavy tier++ |
| ++dev lane caller++ | the dev lane's cdd server | queues ++Run the e2e tier++ |
| ++finishing caller++ | a third process | marks ++Write the scenarios++ (a) done |
| ++reading caller++ | a fourth process | reads the queue while the others change it |
| ++killed caller++ | a process ended while it held the queue's file for a change | none |

### queue files a person must repair

| queue file | holds |
| --- | --- |
| ++cut-off file++ | the first half of the file that held ++Write the scenarios++ and ++Run the unit tier++ |
| ++empty file++ | nothing |
| ++list file++ | `[1, 2]`, a list in place of a queue |
| ++marked file++ | the queue of ++Write the scenarios++ and ++Run the unit tier++, saved by an editor with a byte-order mark at its start |
| ++no-list file++ | `{"prompts": null}` |
| ++no-id file++ | ++Write the scenarios++ (a), then a card with the text Run the unit tier and no id |
| ++shared-id file++ | two cards with the id a |

### chat ids

| chat id | value |
| --- | --- |
| ++chat-1++ | chat-1, the id of the chat whose folder is C:/chats/chat-1 |
| ++escaping chat id++ | `..\escape-chat`, a path to a folder beside the chats folder |
| ++separated chat id++ | `chats/chat-2`, which holds a folder separator |
| ++drive chat id++ | `C:chat-2`, which names a drive |
| ++empty chat id++ | only spaces, from a call that came from no chat |

## Story: Queue Draft Prompt

#### Scenario: Queue the draft as it is at the bottom of the queue

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*And* the prompt box holds the draft ++Run the heavy tier++
*When* the person queues the draft as it is
*Then* the queue holds ++Write the scenarios++, ++Run the unit tier++, then ++Run the heavy tier++
*And* the prompt box is empty

#### Scenario: Keep the queued draft out of the chat

*Given* the person just queued the draft ++Run the heavy tier++ as it is
*When* the chat receives the submission of ++Run the heavy tier++ that follows the key
*Then* the submission is dropped as "Queued for later"
*And* the agent is not sent ++Run the heavy tier++

#### Scenario: Recognise the queued draft whatever line endings it arrives with

*Given* the person just queued the pasted draft ++outstanding items++ with Windows line endings and trailing spaces
*When* the chat receives its submission with plain line endings and a blank last line
*Then* the submission is dropped as "Queued for later"

#### Scenario: Queue nothing for an empty draft

*Given* the chat's prompt queue holds ++Write the scenarios++ (a)
*And* the prompt box holds only spaces
*When* the person queues the draft as it is
*Then* the queue still holds only ++Write the scenarios++

#### Scenario: Keep every caller's change when several change the queue at the same moment

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* ++stable lane caller++, ++dev lane caller++ and ++finishing caller++ change the queue at the same moment
*Then* every caller is answered without a refusal
*And* the queue holds ++Write the scenarios++, done, then ++Run the unit tier++, then ++Run the heavy tier++ and ++Run the e2e tier++ in the order their callers took their turn

#### Scenario: Show a reader the whole queue while another caller changes it

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* ++reading caller++ reads the queue while ++stable lane caller++ changes it
*Then* ++reading caller++ is shown ++Write the scenarios++ and ++Run the unit tier++ at the front of the queue every time it reads

#### Scenario: Take the next change after a caller holding the queue's file is killed

*Given* ++killed caller++ held the queue's file for a change when its process ended
*When* the agent queues ++Run the heavy tier++
*Then* the queue holds ++Run the heavy tier++ at its bottom

#### Scenario: Say the queue's file is held when a change waits for it in vain

*Given* another caller holds the queue's file for a change and does not let go
*When* the agent queues ++Run the heavy tier++
*Then* the agent is told the queue's file is held for a change by another caller, with the file's path
*And* the queue is as it was

## Story: Place Draft Into Plan

#### Scenario: File the draft as a task of the goal it is about

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*And* the prompt box holds the draft ++also run the heavy tier++
*And* the model places it as ++Run the heavy tier too++
*When* the person places the draft into the plan
*Then* the model is asked where ++also run the heavy tier++ belongs, shown each goal with its id, such as [b] Run the unit tier
*And* ++Run the unit tier++ has the step "[interruption] Run the heavy tier too", not started
*And* the queue still holds two cards
*And* the prompt box is empty

#### Scenario: Queue new work as a card of its own, given to no robot

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*And* the prompt box holds the draft ++also run the heavy tier++
*And* the model places it as ++Run the heavy tier card++, naming the robot Bolt
*When* the person places the draft into the plan
*Then* the queue ends with Run the heavy tier, given to no robot
*And* the model was not asked about robots, which Group Queue Into Robots decides

#### Scenario: Keep the draft when the model cannot place it

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*And* the model cannot answer: "the model is busy"
*When* the person places the draft ++also run the heavy tier++ into the plan
*Then* the queue still holds only ++Write the scenarios++ and ++Run the unit tier++
*And* the prompt box still holds ++also run the heavy tier++
*And* the failure line shows "The draft was not placed on the queue: the model is busy"

#### Scenario: Queue each item of a pasted list in order without asking the model

*Given* the chat's prompt queue is empty
*And* the prompt box holds /queue followed by the pasted list ++outstanding items++
*When* the person runs /queue with that list
*Then* the queue holds the three numbered items of ++outstanding items++, in order, without their numbers
*And* the heading Session roots setup is not queued
*And* /queue answers "Queued 3 prompt(s)."
*And* the model is not asked

## Story: Plan Queue From Conversation

#### Scenario: Queue the prompts the model plans from this conversation

Intended: built (`planFromConversation`) but no test or run shows it; the evidence missing is a plugin test or a walk where the model answers a list.

*Given* the chat's prompt queue is empty
*And* the model, reading this conversation, lists ++Write the scenarios++, then ++Run the unit tier++
*When* the person runs /queue with nothing after it
*Then* the queue holds ++Write the scenarios++, then ++Run the unit tier++
*And* the queue opens
*And* /queue answers "Queued 2 prompt(s) from this conversation."

#### Scenario: Say why nothing was queued

*Given* the chat's prompt queue is empty
*And* the model, reading this conversation, answers ++Nothing is left to do++
*When* the person runs /queue with nothing after it
*Then* /queue answers "Queued 0 prompt(s): the model proposed none. It answered: Nothing is left to do."
*And* the queue is still empty

## Story: Attach Images To Queued Prompt

#### Scenario: Keep a queued draft's image beside its prompt

*Given* the chat's prompt queue holds ++Write the scenarios++, queued with ++screenshot.png++ pasted in its draft
*When* the queue attaches ++screenshot.png++ to ++Write the scenarios++
*Then* ++Write the scenarios++ lists one attached file
*And* that file holds ++screenshot.png++'s bytes, named for the prompt

#### Scenario: Refuse an image for a prompt the queue does not hold

*Given* the chat's prompt queue holds ++Write the scenarios++
*When* the queue attaches ++screenshot.png++ to ++missing prompt++
*Then* it is told no prompt z is on the queue

#### Scenario: List each prompt's files for the agent to open

*Given* the prompt queue plays and holds ++Write the scenarios++ (a) with ++a-1.png++ attached, then ++Run the unit tier++ (b) with none
*When* the person sends Fix the Files app
*Then* the queue beside the prompt lists "1. [a] Write the scenarios (attached, open each: C:/chats/chat-1/attachments/a-1.png)"
*And* ++Run the unit tier++ is listed with no files

#### Scenario: Show how many files a card holds

*Given* the chat's prompt queue holds ++Write the scenarios++ (a) with ++a-1.png++ attached, then ++Run the unit tier++ (b) with none
*When* the person opens the prompt queue
*Then* the card of ++Write the scenarios++ shows 📎1
*And* the card of ++Run the unit tier++ shows no 📎

## Story: Open Prompt Queue

#### Scenario: Open the queue as a stack of cards

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*And* the queue is closed, its stack showing 2
*When* the person opens the prompt queue
*Then* a card shows for ++Write the scenarios++, then for ++Run the unit tier++
*And* the open queue and each card fill the chat box's width
*And* each card's buttons sit on a solid dark bar over its right end

#### Scenario: Close the open queue

*Given* the open prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the person closes the prompt queue
*Then* only the stack shows, with its count, 2

#### Scenario: Draw a done prompt dim in its place

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*When* the person opens the prompt queue
*Then* the card of ++Write the scenarios++ shows first, dim
*And* the card of ++Run the unit tier++ is not dim
*And* the stack counts 1 prompt still to do

#### Scenario: Show a queue change that failed on the failure line

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*But* no cdd server answers the chat
*When* the person clears the queue
*Then* the failure line shows failure 1, "The queue did not change: prompt-queue: $.mcp.call: no MCP server plugin:cdd:cdd", from calling prompt-queue.clear on the cdd server, tried as cdd then plugin:cdd:cdd
*And* the queue box shows no failure line or Fix button of its own
*When* the person clears the queue again
*Then* the failure line shows failure 2, so it shows again after Fix or ✕ handled failure 1

## Story: Edit Queued Prompt

#### Scenario: Put a card's prompt in the prompt box to change

*Given* the open prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the person edits ++Run the unit tier++
*Then* the prompt box holds Run the unit tier
*And* the card of ++Run the unit tier++ keeps its place, shaded and marked editing

#### Scenario: Put the changed text back in its place

*Given* the person is editing ++Write the scenarios++ (a)
*And* the prompt box holds ++Write the scenarios again++
*When* the person adds the draft to the queue
*Then* the queue holds ++Write the scenarios again++ as a, then ++Run the unit tier++ (b)

#### Scenario: Leave the prompt being edited out of the queue the agent sees

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*And* the person is editing ++Write the scenarios++
*When* the person sends Fix the Files app
*Then* the queue beside the prompt lists only "1. [b] Run the unit tier"

#### Scenario: Keep a card's text when the changed text is only spaces

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the text of b is changed to only spaces
*Then* the queue still holds ++Write the scenarios++, then ++Run the unit tier++

## Story: Reorder Queued Prompts

#### Scenario: Move a prompt up one place

*Given* the open prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the person moves ++Run the unit tier++ up
*Then* the queue holds ++Run the unit tier++, then ++Write the scenarios++

#### Scenario: Move a prompt down one place

Intended: built (`movePrompt`, `prompt-queue.move`); the evidence missing is a test of the mod's ↓ on a card.

*Given* the open prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the person moves ++Write the scenarios++ down
*Then* the queue holds ++Run the unit tier++, then ++Write the scenarios++

## Story: Remove Queued Prompts

#### Scenario: Remove one prompt, keeping a copy in the queue archive

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the person removes ++Run the unit tier++
*Then* the queue holds only ++Write the scenarios++
*And* the queue archive holds one copy, holding ++Run the unit tier++

#### Scenario: Clear the done prompts first, leaving the work still to do

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*When* the person clears the queue
*Then* the queue holds only ++Run the unit tier++
*And* the queue archive holds one copy, holding ++Write the scenarios++

#### Scenario: Clear every prompt when none is done

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b), neither done
*When* the person clears the queue
*Then* the queue is empty
*And* the queue archive holds one copy, holding ++Write the scenarios++ and ++Run the unit tier++

#### Scenario: Keep the archive in the session's work folder

*Given* the chat works in the session simple-queue, whose work folder is .sessions/simple-queue in the ticket's worktree
*And* its prompt queue holds ++Write the scenarios++
*When* the person clears the queue
*Then* .sessions/simple-queue/queue-archive in the ticket's worktree holds one copy

## Story: Flush Prompt Queue

Requested 2026-11-23 (the person): a flush button that keeps a timestamped copy of the queue file, then takes the finished cards off. Evidence: `tools/prompt_queue/prompt_queue_spec.py`, `prompt_queue_heavy_spec.py`, the plugin tests "flush keeps a copy of the queue as it stood, then takes the finished cards off" and "flush with nothing finished keeps the copy and every card", and `flush-prompt-queue/flush_prompt_queue_story.test.py`.

#### Scenario: Flush keeps a copy of the whole queue file, then takes the done prompts off

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*When* the person flushes the queue
*Then* the queue archive holds a copy of the whole queue file as it stood, named prompt-queue and the time it was flushed
*And* the queue holds only ++Run the unit tier++

#### Scenario: Flush with no prompt done keeps the copy and takes nothing off

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b), neither done
*When* the person flushes the queue
*Then* the queue archive holds one copy of the whole queue file
*And* the queue still holds ++Write the scenarios++, then ++Run the unit tier++

## Story: Refuse Queue File That Holds No Queue

The queue's file is a person's to repair once it is damaged: `JsonFileUnreadable` promises that nothing is written over such a file. Evidence: `tools/prompt_queue/prompt_queue_spec.py`, `harness/installation/json_file_spec.py`.

#### Scenario: Read a queue file saved with a byte-order mark

*Given* the chat's queue file is ++marked file++
*When* the agent queues ++Run the heavy tier++
*Then* the queue holds ++Write the scenarios++, ++Run the unit tier++, then ++Run the heavy tier++

#### Scenario: Refuse to show a queue whose file is damaged

*Given* the chat's queue file is ++cut-off file++
*When* the agent asks for the queue
*Then* the agent is told the prompt queue file does not hold a prompt queue, with the file's path
*And* the agent is not shown an empty queue

Also for ++empty file++ and ++list file++.

#### Scenario: Write nothing over a queue file that is damaged

*Given* the chat's queue file is ++cut-off file++
*When* the agent queues ++Run the heavy tier++
*Then* the agent is told the prompt queue file does not hold a prompt queue, with the file's path
*And* the file still holds what it held, for a person to repair

#### Scenario: Refuse a queue file whose prompts are not a list of cards

*Given* the chat's queue file is ++no-list file++
*When* the agent asks for the queue
*Then* the agent is told the prompt queue file does not hold a prompt queue, with the file's path and what its prompts are

#### Scenario: Refuse a queue file that holds a card with no id

*Given* the chat's queue file is ++no-id file++
*When* the agent marks a done
*Then* the agent is told the prompt queue file does not hold a prompt queue, with the file's path and the card that has no id
*And* ++Write the scenarios++ is not marked done

#### Scenario: Refuse a queue file in which two cards share an id

*Given* the chat's queue file is ++shared-id file++
*When* the agent marks a done
*Then* the agent is told the prompt queue file does not hold a prompt queue, with the file's path and the id the two cards share
*And* neither card is marked done

## Story: Name Queue By Chat Id

A chat's queue is kept in that chat's own folder under the chats folder, so the chat a call names is an id, one folder's name. Evidence: `tools/prompt_queue/prompt_queue_spec.py`, `prompt_queue_heavy_spec.py`.

#### Scenario: Keep a chat's queue in that chat's own folder

*Given* no queue is kept for ++chat-1++
*When* the agent queues ++Write the scenarios++ on the queue of ++chat-1++
*Then* the queue's file is kept in the folder of ++chat-1++ under the chats folder

#### Scenario: Refuse a chat id that is a path

*Given* the chats folder holds no folder for ++escaping chat id++
*When* the agent queues ++Write the scenarios++ on the queue of ++escaping chat id++
*Then* the agent is told ++escaping chat id++ is not a chat id
*And* no queue file is written outside the chats folder

Also for ++separated chat id++, ++drive chat id++ and ++empty chat id++.
