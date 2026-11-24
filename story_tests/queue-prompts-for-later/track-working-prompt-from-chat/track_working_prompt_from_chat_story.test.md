---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Track Working Prompt From Chat

Grouped on 2026-11-24 from Nest Prompt Steps In Queue, which had grown to eleven stories: the prompt being worked follows the chat, taking the agent's task list, while a message the person sends goes to the chat as sent and puts nothing on the queue: the agent decides whether it is work, and files it under its goal or queues it as a card titled cleanly. Rewritten on 2026-11-24 (commit b3d0c6d56): the scenarios in which the mod itself queued a sent prompt, filed a message as an interruption, titled a goal from the message, or told the agent to split a goal beside a message are gone with that behaviour. The queue and its steps stay on the cdd server (`tools/prompt_queue/prompt_queue.py`); the mod (`tools/prompt_queue/hooks/`) copies the agent's task list onto them, files the person's messages, and draws them; the mod's plugin tests (`tools/prompt_queue/hooks/register.test.tsx`) and the server's specs (`tools/prompt_queue/prompt_queue_spec.py`) run them.

### Domain terms

- ++prompt queue++ — the prompts one chat has queued, in order, kept by the cdd server in that chat's own folder.
- ++queued prompt++ — one prompt on the queue, with its id and text.
- ++step++ — one thing the agent plans to do for a queued prompt: its text and its state, pending, being worked, or done.
- ++working prompt++ — the queued prompt the agent was last asked to take, or the prompt the person sent straight to the chat.
- ++task list++ — the agent's own checklist in the desktop chat, set and advanced with `update_plan`.
- ++interruption++ — a message the person sent while a goal was worked, or in answer to the question its turn ended with, filed as that goal's step, its text starting "[interruption]".
- ++goal title++ — what the agent titles a card it queues for a message the person sent: a short statement of the goal in plain words, with the typing mistakes and any venting left out.
- ++talk++ — a message that asks for no work: only marks such as ???, an answer or acknowledgement such as yes or ok, or a short question such as where is the flush button.
- ++board viewer's state++ — what the Claude app puts before a message sent while a board viewer is open: an `<artifact-view-context>` holding the viewer's live state, not typed by the person.
- ++step pointer++ — the mark at the left of a card's first step not done.

> In steps: ++example++ names an example in a table below.

## Examples

### queued prompts

| queued prompt | id | how it reached the queue |
| --- | --- | --- |
| ++Write the scenarios++ | a | queued by the person |
| ++Run the unit tier++ | b | queued by the person |
| ++Fix the Files app++ | sent | sent straight to the chat |

### steps of Write the scenarios

| step | state |
| --- | --- |
| ++Read the epic++ | done |
| ++Write the stories++ | being worked |
| ++Validate the scenarios++ | pending |

### messages the person sends while a goal is worked

| message | text |
| --- | --- |
| ++cut the text++ | cut the text with an ellipsis |
| ++also run the heavy tier++ | also run the heavy tier |
| ++background notice++ | <task-notification> <task-id>b1</task-id> <status>completed</status> </task-notification> |
| ++pasted notes++ | <pasted_content id="7250"> ## Notes from the backlog From `board-enhancements` the board needs a filter. </pasted_content> |
| ++where is flush++ | where is the flush button |
| ++viewer question++ | ++board viewer's state++, then ? |
| ++viewer work++ | ++board viewer's state++, then repin to dev lane |

### gathered steps

| step | state |
| --- | --- |
| ++Read the epic++ | done |
| [interruption] cut the text with an ellipsis | done |
| ++Write the stories++ | done |
| [interruption] Fix the Files app | pending |
| ++Validate the scenarios++ | being worked |
| [interruption] Run the heavy tier | pending |

### robots

| robot | cards |
| --- | --- |
| ++Sparky++ | ++Write the scenarios++ (a) |
| ++Bolt++ | ++Run the unit tier++ (b) |

## Story: Copy Task List Onto Working Prompt

Not yet known: whether a mod's tool-call hook sees the desktop app's `update_plan`. The first two scenarios hold when it does; the third is what happens when it does not.

#### Scenario: Copy the task list onto the working prompt

*Given* the prompt queue plays and the agent was asked to take ++Write the scenarios++ (a)
*When* the agent sets its task list to ++Read the epic++ being worked, ++Write the stories++ pending, ++Validate the scenarios++ pending
*Then* the queue answers ++Write the scenarios++ with those three steps, ++Read the epic++ being worked
*And* the queue box shows ++Write the scenarios++ with them, as in Show Prompt Steps In Queue

#### Scenario: Follow the task list as the agent marks its steps done

*Given* ++Write the scenarios++ (a) is the working prompt with ++Read the epic++ being worked and two steps pending
*When* the agent advances its task list to ++Write the stories++
*Then* the queue answers ++Write the scenarios++ with ++Read the epic++ done and ++Write the stories++ being worked

#### Scenario: Tell the agent to keep the steps itself when its task list cannot be seen

*Given* the queue mod cannot see the agent's task list
*And* the prompt queue plays and holds ++Write the scenarios++ (a)
*When* the person sends ++Fix the Files app++
*Then* the queue beside ++Fix the Files app++ tells the agent to set the steps of ++Write the scenarios++ when it takes it and to mark each one done as it goes

## Story: Queue Sent Prompt As Running

#### Scenario: Leave a background task's notice off the queue

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the chat receives ++background notice++
*Then* the queue still holds only ++Write the scenarios++ and ++Run the unit tier++

#### Scenario: Leave play's own request off the queue

*Given* the prompt queue plays and holds ++Write the scenarios++ (a)
*When* play asks the agent to take the next prompt on the queue
*Then* the queue still holds only ++Write the scenarios++
*And* ++Write the scenarios++ is the working prompt

## Story: Add Interruption To Working Prompt

#### Scenario: Keep the interruption when the agent sets a new task list

*Given* ++Write the scenarios++ (a) is the working prompt with the step "[interruption] cut the text with an ellipsis"
*When* the agent sets its task list to ++Read the epic++ being worked, ++Write the stories++ pending
*Then* the steps of ++Write the scenarios++ still hold "[interruption] cut the text with an ellipsis"

#### Scenario: Show the robots' queues beside a message in sub-agent mode

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*And* ++Write the scenarios++ was the goal last worked
*When* the person sends ++also run the heavy tier++
*Then* the agent reads each robot's queue beside it, such as "Bolt: [b] Run the unit tier"
*And* it is told it decides where the message goes: do it itself, make it a task of an item in a robot's queue, or give it to a robot with prompt-queue.assign

Evidence: plugin test "in sub-agent mode the note on a new message shows the robots' queues and lets the agent decide where it goes" (commit 140dba085).

#### Scenario: Refuse to file a message under a goal the queue does not hold

*Given* the chat's prompt queue holds ++Write the scenarios++ (a)
*But* it holds no prompt with id z
*When* the cdd server is asked to file ++cut the text++ under z
*Then* it is told no prompt z is on the queue

#### Scenario: File nothing for a message of only spaces

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), done, with no steps
*When* a message of only spaces is filed under a
*Then* ++Write the scenarios++ still has no steps
*And* ++Write the scenarios++ is still done

## Story: Title Goal From Sent Message

Built 2026-11-24 (commits 3c5dbc74b, 140dba085, b3d0c6d56): a message goes to the chat as sent and creates no card; the agent puts work on the queue itself, titled cleanly, and the queue keeps only work. Evidence: `tools/prompt_queue/hooks/register.test.tsx` and `tools/prompt_queue/prompt_queue_spec.py`, named under each scenario.

#### Scenario: Put nothing on the queue for a message sent between turns

*Given* the prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*But* no turn runs
*When* the person sends ++Fix the Files app++, or ++pasted notes++
*Then* the queue still holds only ++Write the scenarios++ and ++Run the unit tier++
*And* the agent reads the whole message in the chat

Evidence: plugin tests "a message sent between turns puts nothing on the queue" and "a pasted message puts nothing on the queue".

#### Scenario: Add no step to the working prompt for a message sent mid-work

*Given* a turn runs on ++Write the scenarios++ (a), the working prompt
*When* the person sends ++cut the text++
*Then* ++Write the scenarios++ has no step from the message

Evidence: plugin test "a message sent while a prompt is worked adds no step to it".

#### Scenario: Tell the agent the message is on no card and how to place it

*Given* a turn runs on ++Write the scenarios++ (a), the working prompt, and ++Run the unit tier++ (b) is still to do
*When* the person sends ++cut the text++
*Then* the agent is told the message is on no card of the queue, with the goals still to do and the one being worked, [a]
*And* it is told to answer talk only, to file work for a goal with prompt-queue.add_interruption, and to queue new work with prompt-queue.add, titled as a short statement of the goal with the typing mistakes and venting left out
*And* it is told to call prompt-queue.show and check that what it placed stands once, where it meant it

Evidence: plugin tests "the agent is told the message is on no card and to queue it only when it is work, titled cleanly", "the agent is told the goal being worked when a message is sent mid-work", "the agent is told how to file work under the goal being worked, by its id" and "the agent is told to check the queue after placing the message".

#### Scenario: Answer talk without queueing it

*Given* the prompt queue holds ++Write the scenarios++ (a), the working prompt
*When* the person sends ++where is flush++, "why is there no flush button?", "yes", "ok" or "???", mid-work or between turns
*Then* the queue holds no card and no step from the message

Evidence: plugin tests "a message that is only talk, such as …, sent mid-work is not filed on the queue" and "… sent between turns is not queued", one pair for each message.

#### Scenario: Read talk sent from a board viewer by the person's words alone

*Given* the prompt queue holds ++Write the scenarios++ (a), the working prompt
*When* the person sends ++viewer question++ from an open board viewer
*Then* the message is read as talk, from its "?" alone
*And* the queue holds no card and no step from it, and none titled by the ++board viewer's state++

Evidence: the same two plugin tests, run with the board viewer's state before the "?" (commit 3c5dbc74b).

#### Scenario: Keep a board viewer's state out of a card's title and steps

*Given* the chat's prompt queue holds ++Write the scenarios++ (a)
*When* the cdd server is asked to queue "[interruption] " followed by ++viewer work++
*And* it is asked to file the ++board viewer's state++ followed by "why do the first 2 epics have no sub epics" under a
*Then* the queue's last card reads "[interruption] repin to dev lane"
*And* ++Write the scenarios++ has the step "[interruption] why do the first 2 epics have no sub epics", not started

Evidence: `prompt_queue_spec.py` "queues only the person's words of a card sent from a board viewer" and "files only the person's words of a message sent from a board viewer, leaving out the viewer's state" (commit b123d6925).

#### Scenario: File nothing for a message that holds only a board viewer's state

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), with no steps
*When* the cdd server is asked to file the ++board viewer's state++ alone under a
*Then* ++Write the scenarios++ still has no steps

Evidence: `prompt_queue_spec.py` "files nothing under a goal for a message that holds only a board viewer's state" (commit b123d6925).

## Story: Split Goal Of Interruptions

#### Scenario: Put each interruption still to do on a card of its own

*Given* the prompt queue holds ++Write the scenarios++ (a) with ++gathered steps++, then ++Run the unit tier++ (b)
*When* the person splits ++Write the scenarios++
*Then* the queue holds ++Write the scenarios++, "[interruption] Fix the Files app", "[interruption] Run the heavy tier", then ++Run the unit tier++
*And* ++Write the scenarios++ keeps ++Read the epic++, "[interruption] cut the text with an ellipsis", ++Write the stories++ and ++Validate the scenarios++

#### Scenario: Keep the split cards in the goal's robot's queue

*Given* sub-agent mode is on and ++Bolt++ holds ++Write the scenarios++ (a) with ++gathered steps++
*When* the agent splits ++Write the scenarios++ with prompt-queue.split
*Then* "[interruption] Fix the Files app" and "[interruption] Run the heavy tier" are each given to ++Bolt++

#### Scenario: Offer no split for a goal with no interruption still to do

*Given* the open prompt queue holds ++Run the unit tier++ (b) with no steps
*When* the person points at its card
*Then* its card shows no split among its buttons
*And* the cdd server, asked to split it, changes nothing

#### Scenario: Refuse to split a goal the queue does not hold

*Given* the chat's prompt queue holds ++Write the scenarios++ (a)
*But* it holds no prompt with id z
*When* the agent splits z
*Then* it is told no prompt z is on the queue

