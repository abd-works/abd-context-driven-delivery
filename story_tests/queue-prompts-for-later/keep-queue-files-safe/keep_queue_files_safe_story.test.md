---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Keep Queue Files Safe

Story map: [Keep Queue Files Safe](../../../.context/story-map.md#e-keep-queue-files-safe). The cdd server keeps each chat's prompt queue in one file in that chat's own folder (`tools/prompt_queue/prompt_queue.py`), and every caller, the mod, the agent and both lanes' cdd servers, changes that one file. These stories keep it safe: every caller's change is kept, a file nobody can read is refused and left for a person to repair, and no queue file is written outside the chats folder. They were in Build Prompt Queue until 2026-11-24 (closing choice 13 of the release-1-2-fixes exploratory testing); their scenarios are as they were there. Evidence: the server's specs (`tools/prompt_queue/prompt_queue_spec.py`, `prompt_queue_heavy_spec.py`, `prompt_queue_processes_heavy_spec.py`), unless a scenario says otherwise. No story test file runs them yet.

### Domain terms

- ++prompt queue++ — the prompts one chat has queued, in order, kept by the cdd server in that chat's own folder.
- ++queued prompt++ — one prompt on the queue, drawn as a card: its id, its text, and whether it is done.
- ++queue file++ — the JSON file that holds one chat's prompt queue, in that chat's folder under the chats folder.

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

## Story: Keep Every Caller's Queue Change

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
