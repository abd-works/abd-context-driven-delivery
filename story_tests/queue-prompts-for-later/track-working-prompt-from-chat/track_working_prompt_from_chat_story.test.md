---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Track Working Prompt From Chat

Grouped on 2026-11-24 from Nest Prompt Steps In Queue, which had grown to eleven stories: the prompt being worked follows the chat, taking the agent's task list, the prompts the person sends straight to the chat, and the messages the person sends while a goal is worked, titled by what they ask. The queue and its steps stay on the cdd server (`tools/prompt_queue/prompt_queue.py`); the mod (`tools/prompt_queue/hooks/`) copies the agent's task list onto them, files the person's messages, and draws them; the mod's plugin tests (`tools/prompt_queue/hooks/register.test.tsx`) and the server's specs (`tools/prompt_queue/prompt_queue_spec.py`) run them.

### Domain terms

- ++prompt queue++ — the prompts one chat has queued, in order, kept by the cdd server in that chat's own folder.
- ++queued prompt++ — one prompt on the queue, with its id and text.
- ++step++ — one thing the agent plans to do for a queued prompt: its text and its state, pending, being worked, or done.
- ++working prompt++ — the queued prompt the agent was last asked to take, or the prompt the person sent straight to the chat.
- ++task list++ — the agent's own checklist in the desktop chat, set and advanced with `update_plan`.
- ++interruption++ — a message the person sent while a goal was worked, or in answer to the question its turn ended with, filed as that goal's step, its text starting "[interruption]".
- ++goal title++ — what the queue holds for a message the person sent: the first sentence of their own words, or a paste's first line, at most 80 characters, never the paste or its `<pasted_content>` tags.
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

#### Scenario: Put a prompt sent straight to the chat on the queue as the working prompt

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*But* no goal was worked yet
*When* the person sends ++Fix the Files app++ straight to the chat
*Then* the queue holds "[interruption] Fix the Files app" first, then ++Write the scenarios++, then ++Run the unit tier++
*And* the agent is told the prompt is on the queue as its id, to mark it done when its work is done
*And* "[interruption] Fix the Files app" is the working prompt its steps are copied onto, as in Copy Task List Onto Working Prompt

#### Scenario: Put a sent prompt above the next prompt to do, below the done ones

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*But* no goal was worked yet
*When* the person sends ++Fix the Files app++ straight to the chat
*Then* the queue holds ++Write the scenarios++, "[interruption] Fix the Files app", then ++Run the unit tier++

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

#### Scenario: File a message sent mid-work under the working prompt

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*And* a turn runs on ++Write the scenarios++, the working prompt
*When* the person sends ++cut the text++
*Then* ++Write the scenarios++ has the step "[interruption] cut the text with an ellipsis", not started
*And* the queue still holds only ++Write the scenarios++ and ++Run the unit tier++
*And* the agent is told the queue filed it under the goal last worked, [a], and to decide before any other work where it belongs, with each goal on the queue listed, such as [b] Run the unit tier

#### Scenario: Open a done goal again for an answer to the agent's question sent between turns

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*And* ++Write the scenarios++ was the goal last worked, and its turn ended asking the person something
*But* no turn runs
*When* the person sends ++cut the text++
*Then* ++Write the scenarios++ is no longer done and has the step "[interruption] cut the text with an ellipsis", not started
*And* the queue still holds only ++Write the scenarios++ and ++Run the unit tier++

#### Scenario: Start a goal of its own for new work sent between turns

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*And* ++Write the scenarios++ was the goal last worked, and its turn ended asking nothing
*But* no turn runs
*When* the person sends ++Fix the Files app++ straight to the chat
*Then* the queue holds "[interruption] Fix the Files app" first, as the working prompt, then ++Write the scenarios++, then ++Run the unit tier++
*And* ++Write the scenarios++ has no step from the message
*And* the agent is told the prompt is on the queue as its id, and to make it a task of a goal it belongs to or mark it done when its work is done

#### Scenario: Keep the interruption when the agent sets a new task list

*Given* ++Write the scenarios++ (a) is the working prompt with the step "[interruption] cut the text with an ellipsis"
*When* the agent sets its task list to ++Read the epic++ being worked, ++Write the stories++ pending
*Then* the steps of ++Write the scenarios++ still hold "[interruption] cut the text with an ellipsis"

#### Scenario: Show the robots' queues beside a message in sub-agent mode

*Given* sub-agent mode is on, ++Sparky++ holding ++Write the scenarios++ (a) and ++Bolt++ holding ++Run the unit tier++ (b)
*And* ++Write the scenarios++ was the goal last worked
*When* the person sends ++also run the heavy tier++
*Then* the agent reads each robot's queue beside it, such as "Bolt: [b] Run the unit tier"
*And* it is told it decides where the message goes: do it itself, make it a task of an item in a robot's queue, or give it to a robot as a new item starting "[for <robot name>]"

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

#### Scenario: Title a goal sent as pasted text by its first line, never the paste

*Given* the chat's prompt queue is empty
*When* the person's first message is ++pasted notes++
*Then* the queue holds one goal, "[interruption] Notes from the backlog", without the paste or its tags
*And* the agent still reads the whole message in the chat

#### Scenario: Title a goal by the person's own words beside a paste

*Given* the chat's prompt queue is empty
*When* the person sends "Triage these notes into the backlog" with ++pasted notes++ below it
*Then* the queue holds one goal, "[interruption] Triage these notes into the backlog"

#### Scenario: Title a long goal by its first sentence, cut short

*Given* the chat's prompt queue is empty
*When* the person sends a message whose first sentence is longer than 80 characters
*Then* the goal's title is that sentence cut at a word, at most 80 characters, ending in an ellipsis

#### Scenario: Gather no later messages under a pasted first message

*Given* the person's first message was ++pasted notes++, queued as "[interruption] Notes from the backlog"
*When* the person sends ++Fix the Files app++, then ++Run the unit tier++, each between turns
*Then* each is a goal of its own on the queue
*And* "[interruption] Notes from the backlog" has no steps

#### Scenario: Title a pasted message sent mid-work by its first line

*Given* a turn runs on ++Write the scenarios++, the working prompt
*When* the person sends ++pasted notes++
*Then* ++Write the scenarios++ has the step "[interruption] Notes from the backlog", not started

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

#### Scenario: Tell the agent it can split a goal that gathered other work

*Given* a turn runs on ++Write the scenarios++, the working prompt
*When* the person sends ++cut the text++
*Then* the agent is told, beside the message, to split a goal's interruptions about other work onto cards of their own with prompt-queue.split
