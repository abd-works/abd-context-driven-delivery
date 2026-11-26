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
