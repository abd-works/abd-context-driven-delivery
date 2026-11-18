---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Nest Prompt Steps In Queue

Agreed with the person on 2026-11-17 and built the same day: the server's specs (`tools/prompt_queue/prompt_queue_spec.py`), the story tests of Set Steps Of Queued Prompt and Tick Off Prompt Step, and the mod's plugin tests (`tools/prompt_queue/hooks/register.test.tsx`) run them; Copy Task List Onto Working Prompt says what is not yet known. The queue and its steps stay on the cdd server (`tools/prompt_queue/prompt_queue.py`); the mod (`tools/prompt_queue/hooks/`) copies the agent's task list onto them and draws them.

### Domain terms

- ++prompt queue++ — the prompts one chat has queued, in order, kept by the cdd server in that chat's own folder.
- ++queued prompt++ — one prompt on the queue, with its id and text.
- ++step++ — one thing the agent plans to do for a queued prompt: its text and its state, pending, being worked, or done.
- ++working prompt++ — the queued prompt the agent was last asked to take, or the prompt the person sent straight to the chat.
- ++task list++ — the agent's own checklist in the desktop chat, set and advanced with `update_plan`.
- ++interruption++ — a message the person sent while a goal was worked, filed as that goal's step, its text starting "[interruption]".
- ++step pointer++ — the mark at the left of a card's first step not done.

> In steps: ++example++ names an example in a table below.

## Examples

### queued prompts

| example | id | how it reached the queue |
| --- | --- | --- |
| ++Write the scenarios++ | a | queued by the person |
| ++Run the unit tier++ | b | queued by the person |
| ++Fix the Files app++ | sent | sent straight to the chat |

### steps of Write the scenarios

| example | state |
| --- | --- |
| ++Read the epic++ | done |
| ++Write the stories++ | being worked |
| ++Validate the scenarios++ | pending |

### steps the person changes

| example | state |
| --- | --- |
| ++Write them++ | being worked, after Read the epic done |
| ++Validate them++ | pending |
| ++Render the map++ | the prompt box's draft, added as a step |
| ++Write them all++ | the prompt box's draft, made a step's text |

### messages the person sends while a goal is worked

| example | text |
| --- | --- |
| ++cut the text++ | cut the text with an ellipsis |
| ++also run the heavy tier++ | also run the heavy tier |
| ++background notice++ | <task-notification> <task-id>b1</task-id> <status>completed</status> </task-notification> |

### robots

| example | cards |
| --- | --- |
| ++Sparky++ | ++Write the scenarios++ (a) |
| ++Bolt++ | ++Run the unit tier++ (b) |

## Story: Set Steps Of Queued Prompt

#### Scenario: Give a queued prompt its steps

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*But* ++Write the scenarios++ has no steps
*When* the agent sets the steps of a to ++Read the epic++, ++Write the stories++, ++Validate the scenarios++, each pending
*Then* the queue answers ++Write the scenarios++ with those three steps, in that order, none done
*And* ++Run the unit tier++ still has no steps

#### Scenario: Keep each step's state as given

*Given* the chat's prompt queue holds ++Write the scenarios++ (a)
*When* the agent sets the steps of a to ++Read the epic++ done, ++Write the stories++ being worked, ++Validate the scenarios++ pending
*Then* the queue answers ++Write the scenarios++ with ++Read the epic++ done, ++Write the stories++ being worked and ++Validate the scenarios++ pending

#### Scenario: Replace the steps a prompt had

*Given* ++Write the scenarios++ (a) has the steps ++Read the epic++, ++Write the stories++, ++Validate the scenarios++
*When* the agent sets the steps of a to ++Read the epic++ done, ++Validate the scenarios++ pending
*Then* the queue answers ++Write the scenarios++ with only ++Read the epic++ done and ++Validate the scenarios++ pending

#### Scenario: Refuse steps for a prompt the queue does not hold

*Given* the chat's prompt queue holds ++Write the scenarios++ (a)
*But* it holds no prompt with id z
*When* the agent sets the steps of z
*Then* the agent is told no prompt z is on the queue
*And* the queue still holds ++Write the scenarios++ with no steps

## Story: Tick Off Prompt Step

#### Scenario: Mark one step done

*Given* ++Write the scenarios++ (a) has three steps, none done
*When* the agent marks the first step of a done
*Then* the queue answers ++Write the scenarios++ with ++Read the epic++ done and the other two not done

#### Scenario: Leave the prompt on the queue once every step is done

*Given* ++Write the scenarios++ (a) has three steps, two of them done
*When* the agent marks the last step of a done
*Then* the queue answers ++Write the scenarios++ with every step done
*And* ++Write the scenarios++ stays on the queue until the agent marks it done with prompt-queue.done, as in Work Through Prompt Queue

#### Scenario: Refuse a step the prompt does not have

*Given* ++Write the scenarios++ (a) has three steps
*When* the agent marks step 4 of a done
*Then* the agent is told ++Write the scenarios++ has three steps
*And* ++Write the scenarios++ still has no step done

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

#### Scenario: Open a done goal again for a message sent between turns

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*And* ++Write the scenarios++ was the goal last worked
*But* no turn runs
*When* the person sends ++cut the text++
*Then* ++Write the scenarios++ is no longer done and has the step "[interruption] cut the text with an ellipsis", not started
*And* the queue still holds only ++Write the scenarios++ and ++Run the unit tier++

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

## Story: Show Prompt Steps In Queue

#### Scenario: Show each card's progress

*Given* the prompt queue holds ++Write the scenarios++ (a) with one of three steps done, then ++Run the unit tier++ (b) with no steps
*When* the person opens the prompt queue
*Then* ++Write the scenarios++' card shows 1/3
*And* ++Run the unit tier++'s card shows no progress

#### Scenario: Show a prompt's steps under its card

*Given* the open prompt queue holds ++Write the scenarios++ (a) with ++Read the epic++ done, ++Write the stories++ being worked, ++Validate the scenarios++ pending
*When* the person opens the steps of ++Write the scenarios++
*Then* ++Read the epic++, ++Write the stories++ and ++Validate the scenarios++ show under its card, in order
*And* ++Read the epic++ is ticked and ++Write the stories++ is marked as being worked

#### Scenario: Fold a prompt's steps away

*Given* the steps of ++Write the scenarios++ show under its card
*When* the person closes them
*Then* only the card of ++Write the scenarios++ shows, with 1/3

## Story: Edit Prompt Steps

#### Scenario: Add the draft as a card's first step

*Given* the open prompt queue holds ++Write the scenarios++ (a) with three steps, then ++Run the unit tier++ (b) with none
*And* the prompt box holds ++Render the map++
*When* the person adds a step to ++Run the unit tier++
*Then* ++Run the unit tier++ has the one step ++Render the map++, not started
*And* the prompt box is empty
*And* the steps of ++Run the unit tier++ show under its card

#### Scenario: Take a step off its prompt

*Given* the steps of ++Write the scenarios++ (a) show under its card: ++Read the epic++, ++Write the stories++, ++Validate them++
*When* the person removes ++Write the stories++
*Then* ++Write the scenarios++ has the steps ++Read the epic++, then ++Validate them++

#### Scenario: Move a step one place

*Given* the steps of ++Write the scenarios++ (a) show under its card: ++Read the epic++, ++Write the stories++, ++Validate them++
*When* the person moves ++Validate them++ up
*Then* the steps are ++Read the epic++, ++Validate them++, ++Write the stories++
*When* the person moves ++Read the epic++ down
*Then* the steps are ++Validate them++, ++Read the epic++, ++Write the stories++

#### Scenario: Take a step's text into the empty prompt box to change

*Given* the steps of ++Write the scenarios++ (a) show under its card: ++Read the epic++ done, ++Write them++ being worked
*And* the prompt box is empty
*When* the person edits ++Write them++
*Then* the prompt box holds Write them

#### Scenario: Make the draft a step's text

*Given* the steps of ++Write the scenarios++ (a) show under its card: ++Read the epic++ done, ++Write them++ being worked
*And* the prompt box holds ++Write them all++
*When* the person edits ++Write them++
*Then* ++Write the scenarios++ has the steps ++Read the epic++, then ++Write them all++
*And* the prompt box is empty

## Story: Send Prompt Step Now

#### Scenario: Send one step of a prompt to the chat at once

*Given* the steps of ++Write the scenarios++ (a) show under its card: ++Read the epic++ done, ++Write them++ being worked
*When* the person sends ++Write them++ now
*Then* the chat is sent "Take step 2 of prompt [a] on the queue now: Write them"
*And* ++Write the scenarios++ is the working prompt

## Story: Move Step Pointer

#### Scenario: Move the step pointer up to work a done step again

*Given* the steps of ++Write the scenarios++ (a) show under its card: ++Read the epic++ done, ++Write them++ being worked
*And* the step pointer stands at ++Write them++
*When* the person moves the step pointer up
*Then* ++Read the epic++ is being worked and ++Write them++ is not started

#### Scenario: Move the step pointer down to finish its step

*Given* the steps of ++Write the scenarios++ (a) show under its card: ++Read the epic++ done, ++Write them++ being worked, ++Validate them++ pending
*When* the person moves the step pointer down
*Then* ++Read the epic++ and ++Write them++ are done
*And* ++Validate them++ is being worked
