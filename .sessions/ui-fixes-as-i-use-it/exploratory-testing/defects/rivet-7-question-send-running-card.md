# Question: should sending the card being worked (the main chat's or a robot's running card) to another chat be refused or warned?

- **Charter:** C2
- **Tester:** Rivet
- **Story:** no scenario covers send_to_chat. Charter C2 names "a card sent while it is the running one".
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue.send_to_chat` (knows nothing of the running card); band `sendSelectedToChat` and `forgetRobotsNoCardNames` in `tools/prompt_queue/hooks/queue/prompt-queue.ts`.
- **Severity:** question

## Steps

1. Queue on, sub-agent mode on, robot Bolt's sub-agent working card A (or the main chat working A after play / send now: `askedAbout` = A).
2. Select A (☐), send to another connected chat.

## What happens (by reading and by running the Python)

`send_to_chat` takes A off this queue and sends it, with no check. Here, the work goes on: the main agent's plan stops being copied (`copyPlanOntoWorkingPrompt` returns when A is gone), its `prompt-queue.done(A)` is refused with "was taken off the queue at ...", and when A was Bolt's last card `forgetRobotsNoCardNames` forgets Bolt's sub-agent while it still runs, so its row and its "stopped short" check-in vanish. There, the other chat files A as not done (or with the steps as they stood) and works it again. The work is done twice, and this chat's record of the first run is lost.

## Question

Is sending a running card meant to hand the work over (then the running agent here should be told to stop), or should it be refused / asked about while the card is being worked?

## Triage

- **Status:** question for the person. No behaviour changed.
- **Severity:** question.
- **Triaged by:** Cue
- **What the sources say:** the person's ask (`.sessions/_backlog/chat-ui-defects.md`, "The queue band cannot hand cards to another chat") and `PromptQueue.send_to_chat`'s doc both say cards are sent "done or not", and say nothing of a card that is being worked; no scenario covers sending (the scenarios written in this round, under Send Queued Prompts To Another Chat in `share_queue_among_robots_story.test.md`, do not either). The cdd server cannot tell the running card (the band holds `askedAbout` and each robot's working sub-agent), so any check belongs to the band (`sendSelectedToChat` in `tools/prompt_queue/hooks/queue/prompt-queue.ts`).
- **Recommendation:** refuse, with a reason, rather than hand the work over silently: the band leaves the card being worked (the main chat's `askedAbout`, or a robot's card whose sub-agent is running) out of what it sends and says "<card> is being worked here: wait for it to finish, or stop it, then send it". Handing over would need this chat to stop its running agent and a robot's sub-agent, which no tool does today, and without that the work is done twice and this chat's record of the first run is lost, as the report shows.
