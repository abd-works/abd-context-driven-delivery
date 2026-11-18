---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Work Through Prompt Queue

The agent works through the queue in order and marks each prompt done; the person sets the pace with play, pause, send now and the queue's pointer. Evidence: `tools/prompt_queue/prompt_queue_spec.py`, `prompt_queue_heavy_spec.py`, `space/session` specs for handoffs, and the mod's plugin tests (`tools/prompt_queue/hooks/register.test.tsx`), unless a scenario says otherwise.

### Domain terms

- ++prompt queue++ — the prompts one chat has queued, in order, kept by the cdd server in that chat's own folder (`tools/prompt_queue/prompt_queue.py`).
- ++done++ — the agent has finished a prompt's work and marked it with prompt-queue.done; it stays in its place, drawn dim, until the queue is cleared, and play skips it.
- ++play++ — while the queue plays, every prompt carries the queue beside it and every finished turn asks the agent to take the next prompt; paused, the queue waits.
- ++working prompt++ — the queued prompt the agent was last asked to take, or last gave steps to.
- ++pointer++ — the mark at the left of the next card to do, the first card neither done nor marked [decision required].
- ++decision required++ — a prompt put back on the queue to wait for the person's answer; its text starts "[decision required]" and play passes over it.

> In steps: ++example++ names an example in a table below.

## Examples

### queued prompts

| example | id |
| --- | --- |
| ++Write the scenarios++ | a |
| ++Run the unit tier++ | b |
| ++/actions-generate stories-story-map format=drawio++ | c, a queued slash command |
| ++[decision required] Which failure route? A or B++ | a, put back to wait for an answer |

### messages the person sends

| example | why |
| --- | --- |
| ++Fix the Files app++ | a prompt sent straight to the chat |
| ++Which way?++ | the question the agent's wrap-up ends its turn with |
| ++Take the first way++ | the person's answer |

### what play sends

| example | text |
| --- | --- |
| ++ask for the next prompt++ | Take the next prompt on the queue. |
| ++decision timed out++ | No answer came within a minute. Put prompt [a] back on the queue as unfinished: give it with prompt-queue.edit a text that starts with "[decision required]", then the question and your recommendation. Then take the next prompt on the queue. |

## Story: Queue Prompts Through The Cdd Server

#### Scenario: Queue a list of work on the agent's own chat

*Given* the agent's chat has an empty prompt queue
*When* the agent calls prompt-queue.add_all with Write the scenarios and Run the unit tier, naming no chat
*Then* its chat's prompt queue holds Write the scenarios, then Run the unit tier

#### Scenario: Mark a prompt done once its work is done

*Given* the agent's chat queue holds Write the scenarios, then Run the unit tier
*When* the agent calls prompt-queue.done with the id of Write the scenarios
*Then* its chat's prompt queue still holds Write the scenarios, marked done, then Run the unit tier
*And* clearing the queue takes off Write the scenarios and leaves Run the unit tier

#### Scenario: Keep each chat's queue apart

*Given* the agent's chat queue holds Run the unit tier
*When* another chat in the same project reads its prompt queue
*Then* that queue is empty

## Story: Queue Handoff Steps On Session Start

#### Scenario: Queue the handoff's steps when a chat switches to its session

*Given* session alpha's latest handoff lists Read the handoff, then Run the unit tier under Approach for Next Agent
*When* a chat switches to alpha
*Then* the chat's prompt queue holds Read the handoff, then Run the unit tier
*And* the switch tells the agent to work through them, marking each one done

#### Scenario: Queue a handoff once

*Given* a chat switched to alpha and its prompt queue holds alpha's two handoff steps
*When* the chat switches to alpha again
*Then* its prompt queue still holds two prompts

## Story: Show Prompt Queue To Agent

#### Scenario: Carry the queue beside each prompt while it plays

*Given* the prompt queue plays and holds Write the scenarios, then Run the unit tier
*When* the Person sends Fix the Files app
*Then* the agent reads the queue beside the prompt, in order, with each prompt's id
*And* it is told to finish its work, then take the first prompt, and mark each one done

#### Scenario: Carry no queue while paused

*Given* the prompt queue is paused and holds Write the scenarios
*When* the Person sends Fix the Files app
*Then* the agent reads no queue beside the prompt

#### Scenario: Leave out the prompts already done

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*When* the person sends ++Fix the Files app++
*Then* the queue beside the prompt lists ++Run the unit tier++
*And* it does not list ++Write the scenarios++

#### Scenario: Tell the agent to keep one card for each goal

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the person sends ++Fix the Files app++
*Then* the queue beside the prompt tells the agent to keep one card for each goal
*And* to make a message that belongs to a goal already on the queue a task of that goal

## Story: Play Prompt Queue

#### Scenario: Ask for the next prompt when play is pressed

*Given* the prompt queue is paused and holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*But* no turn is running
*When* the person plays the queue
*Then* the chat is sent ++ask for the next prompt++
*And* the queue still holds ++Write the scenarios++, then ++Run the unit tier++

#### Scenario: Ask for the next prompt when a turn ends

*Given* the prompt queue plays and holds Write the scenarios
*When* a turn ends
*Then* the chat is sent Take the next prompt on the queue
*And* Write the scenarios stays on the queue until the agent marks it done

#### Scenario: Pass over done prompts

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*And* the agent was last asked to take ++Write the scenarios++
*When* a turn ends
*Then* the chat is sent ++ask for the next prompt++, for ++Run the unit tier++

#### Scenario: Run a queued slash command as the command

*Given* the open prompt queue holds only ++/actions-generate stories-story-map format=drawio++ (c)
*When* the person plays the queue
*Then* the chat runs the command actions-generate with stories-story-map format=drawio, not a prompt
*And* ++/actions-generate stories-story-map format=drawio++ is marked done

#### Scenario: Pause when the agent left the prompt it was asked to take

*Given* the agent was asked to take Write the scenarios and it is still first on the queue
*When* the turn ends
*Then* the queue pauses and says the agent left Write the scenarios on the queue

## Story: Pause Prompt Queue

#### Scenario: Stop asking for the next prompt once paused

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*When* the person pauses the queue
*Then* the play button offers to play again
*When* a turn ends
*Then* the chat is sent nothing
*And* the queue still holds ++Write the scenarios++, then ++Run the unit tier++

## Story: Wait For Answer Before Moving On

#### Scenario: Wait a minute when a turn ends with a question

*Given* the prompt queue plays and holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*And* the agent was asked to take ++Write the scenarios++
*And* the agent's wrap-up asks the person ++Which way?++
*When* the turn ends
*Then* the chat is sent nothing
*And* play waits one minute for the answer

#### Scenario: Put the prompt back as needing a decision when no answer comes

*Given* play waits for the answer to ++Which way?++ on ++Write the scenarios++ (a)
*When* the minute passes with no answer
*Then* the chat is sent ++decision timed out++, naming prompt [a]

#### Scenario: End the wait when the person answers

*Given* play waits for the answer to ++Which way?++ on ++Write the scenarios++ (a)
*When* the person answers ++Take the first way++ within the minute
*Then* the chat is sent nothing when the minute passes

#### Scenario: Pass over a prompt that waits for a decision

*Given* the prompt queue plays and holds ++[decision required] Which failure route? A or B++ (a), then ++Run the unit tier++ (b)
*When* the person sends ++Fix the Files app++
*Then* the queue beside the prompt lists only "1. [b] Run the unit tier"

## Story: Send Queued Prompt Now

#### Scenario: Send a card to the chat at once

*Given* the open prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)
*But* the queue does not play
*When* the person sends ++Run the unit tier++ now
*Then* the queue holds ++Run the unit tier++, then ++Write the scenarios++
*And* the chat is sent "Take prompt [b] on the queue now: Run the unit tier"
*And* ++Run the unit tier++ is the working prompt, so its steps follow the agent's task list, as in Copy Task List Onto Working Prompt

## Story: Move Queue Pointer

#### Scenario: Point at the next card to do

*Given* the open prompt queue holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*When* the person opens the prompt queue
*Then* the pointer stands at the left of ++Run the unit tier++, and of no other card
*And* the orange working mark is on ++Run the unit tier++'s card

#### Scenario: Move the pointer up to run a done card again

*Given* the open prompt queue holds ++Write the scenarios++ (a), done, with its step Write them done, then ++Run the unit tier++ (b)
*When* the person moves the pointer up
*Then* ++Write the scenarios++ is no longer done and its step Write them is not started
*And* the pointer stands at ++Write the scenarios++, so play runs it again

#### Scenario: Move the pointer down to pass a card

*Given* the open prompt queue holds ++Write the scenarios++ (a), done, then ++Run the unit tier++ (b)
*When* the person moves the pointer down
*Then* ++Run the unit tier++ is done, so play moves past it

#### Scenario: Move the pointer up from under the last card

*Given* the open prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b), both done
*And* the pointer stands under ++Run the unit tier++
*When* the person moves the pointer up
*Then* ++Run the unit tier++ is no longer done
*And* ++Write the scenarios++ is still done

#### Scenario: Keep the working mark on the pointer's card

*Given* the open prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b), neither done
*And* the agent last touched ++Run the unit tier++
*When* the person opens the prompt queue
*Then* the orange working mark is on ++Write the scenarios++'s card, where the pointer stands
*And* ++Run the unit tier++'s card has no working mark
