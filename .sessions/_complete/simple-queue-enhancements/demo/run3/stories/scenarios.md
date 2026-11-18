# Queue Prompts For Later: scenarios by sub-epic

Scenarios per sub-epic: build-prompt-queue 27, nest-prompt-steps-in-queue 30, share-queue-among-robots 15, work-through-prompt-queue 25 (97 in all).
Most scenarios: nest-prompt-steps-in-queue, with 30.

The scenario titles under each story come from the sub-epic's `*_story.test.md`; the `*_story.test.py` files in its story folders hold the same scenarios as executable tests.

## build-prompt-queue

Summary: The person can queue a draft (or a pasted list) without sending it, have the model file it under the right goal, attach images to it, and open, edit, reorder, and remove cards, with removed ones kept in an archive.

Files: `build-prompt-queue/attach-images-to-queued-prompt/attach_images_to_queued_prompt_story.test.py`, `build-prompt-queue/build_prompt_queue_story.test.md`

### Queue Draft Prompt

- Queue the draft as it is at the bottom of the queue
- Keep the queued draft out of the chat
- Recognise the queued draft whatever line endings it arrives with
- Queue nothing for an empty draft

### Place Draft Into Plan

- File the draft as a task of the goal it is about
- Queue new work as a card of its own, given to no robot
- Keep the draft when the model cannot place it
- Queue each item of a pasted list in order without asking the model

### Plan Queue From Conversation

- Queue the prompts the model plans from this conversation
- Say why nothing was queued

### Attach Images To Queued Prompt

- Keep a queued draft's image beside its prompt
- Refuse an image for a prompt the queue does not hold
- List each prompt's files for the agent to open
- Show how many files a card holds

### Open Prompt Queue

- Open the queue as a stack of cards
- Close the open queue
- Draw a done prompt dim in its place
- Show a queue change that failed on the failure line

### Edit Queued Prompt

- Put a card's prompt in the prompt box to change
- Put the changed text back in its place
- Leave the prompt being edited out of the queue the agent sees

### Reorder Queued Prompts

- Move a prompt up one place
- Move a prompt down one place

### Remove Queued Prompts

- Remove one prompt, keeping a copy in the queue archive
- Clear the done prompts first, leaving the work still to do
- Clear every prompt when none is done
- Keep the archive in the session's work folder

## nest-prompt-steps-in-queue

Summary: Each queued prompt carries the agent's own steps for it: the agent sets and ticks them, its task list is copied on, messages sent mid-work file under the working prompt, and the person can see, edit, send, and re-point those steps.

Files: `nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md`, `nest-prompt-steps-in-queue/set-steps-of-queued-prompt/set_steps_of_queued_prompt_story.test.py`, `nest-prompt-steps-in-queue/tick-off-prompt-step/tick_off_prompt_step_story.test.py`

### Set Steps Of Queued Prompt

- Give a queued prompt its steps
- Keep each step's state as given
- Replace the steps a prompt had
- Refuse steps for a prompt the queue does not hold

### Tick Off Prompt Step

- Mark one step done
- Leave the prompt on the queue once every step is done
- Refuse a step the prompt does not have

### Copy Task List Onto Working Prompt

- Copy the task list onto the working prompt
- Follow the task list as the agent marks its steps done
- Tell the agent to keep the steps itself when its task list cannot be seen

### Queue Sent Prompt As Running

- Put a prompt sent straight to the chat on the queue as the working prompt
- Put a sent prompt above the next prompt to do, below the done ones
- Leave a background task's notice off the queue
- Leave play's own request off the queue

### Add Interruption To Working Prompt

- File a message sent mid-work under the working prompt
- Open a done goal again for a message sent between turns
- Keep the interruption when the agent sets a new task list
- Show the robots' queues beside a message in sub-agent mode
- Refuse to file a message under a goal the queue does not hold

### Show Prompt Steps In Queue

- Show each card's progress
- Show a prompt's steps under its card
- Fold a prompt's steps away

### Edit Prompt Steps

- Add the draft as a card's first step
- Take a step off its prompt
- Move a step one place
- Take a step's text into the empty prompt box to change
- Make the draft a step's text

### Send Prompt Step Now

- Send one step of a prompt to the chat at once

### Move Step Pointer

- Move the step pointer up to work a done step again
- Move the step pointer down to finish its step

## share-queue-among-robots

Summary: The work still to do can be split among named robots, each card keeps its robot across reloads, one sub-agent starts per robot, and each robot can be renamed and its queue collapsed or expanded.

Files: `share-queue-among-robots/share_queue_among_robots_story.test.md`

### Group Queue Into Robots

- Give each card its robot
- Group only the work not done
- Name new robots apart from the robots already on the queue
- Show a card queued for a robot by name in that robot's queue

### Assign Queued Prompt To Robot

- Keep a card's robot on the queue
- Take a card off its robot
- Bring each robot's queue back after a reload

### Send Queued Prompts To Sub-Agents

- Start one sub-agent for each robot
- Keep a robot's finished work dim in its queue
- Work a robot's card as a card of the single queue

### Rename Robot

- Name a robot from the prompt box
- Start the sub-agent with its robot's new name

### Collapse Robot Queue

- Collapse a robot's queue to the robot alone
- Show how many of a collapsed robot's items are done
- Expand a collapsed robot's queue

## work-through-prompt-queue

Summary: The agent works the queue through the cdd server: play sends the next prompt not done after each turn, pause stops it, done and decision-waiting prompts are passed over, and the person can send a card at once or move the pointer to choose what runs next.

Files: `work-through-prompt-queue/work_through_prompt_queue_story.test.md`

### Queue Prompts Through The Cdd Server

- Queue a list of work on the agent's own chat
- Mark a prompt done once its work is done
- Keep each chat's queue apart

### Queue Handoff Steps On Session Start

- Queue the handoff's steps when a chat switches to its session
- Queue a handoff once

### Show Prompt Queue To Agent

- Carry the queue beside each prompt while it plays
- Carry no queue while paused
- Leave out the prompts already done
- Tell the agent to keep one card for each goal

### Play Prompt Queue

- Ask for the next prompt when play is pressed
- Ask for the next prompt when a turn ends
- Pass over done prompts
- Run a queued slash command as the command
- Pause when the agent left the prompt it was asked to take

### Pause Prompt Queue

- Stop asking for the next prompt once paused

### Wait For Answer Before Moving On

- Wait a minute when a turn ends with a question
- Put the prompt back as needing a decision when no answer comes
- End the wait when the person answers
- Pass over a prompt that waits for a decision

### Send Queued Prompt Now

- Send a card to the chat at once

### Move Queue Pointer

- Point at the next card to do
- Move the pointer up to run a done card again
- Move the pointer down to pass a card
- Move the pointer up from under the last card
- Keep the working mark on the pointer's card
