# Report — Rivet, charter C2 (queue band: robot rows, themes, + then send, send to another chat)

Sandbox `...\scratchpad\et\queue\` (notes in `sandbox\notes.md`). Chats folder and home were throwaway; chats `lead-aaa`, `other-bbb`, `lead`, `other`, `b1`, `b2`, `t-themes` were made up and checked in through `Chat.check_in`. No real chat was touched except the `[defect]` cards on the supervisor's queue.

## What I tested

- **Python, run for real:** `PromptQueue.add_all`, `assign`, `set_theme`, `set_steps`, `done`, `attach`, `send_to_chat` in a throwaway chats folder. Refusals of send_to_chat (no card, own chat with and without spaces, unknown chat, path chat id, one id not held, chat id with a trailing space); order and duplicate ids; resend of a sent card; four processes racing to send one card to two chats; a failure after delivery; multi-line card text; attachments; theme spellings, empty and multi-line themes. `prompt_queue_spec.py`: 115 examples pass.
- **TypeScript, read only:** `prompt-queue.ts` (`addStep`, `takeAwaitedStep`, `changeQueue`, `sendSelectedToChat`, `forgetRobotsNoCardNames`, `copyPlanOntoWorkingPrompt`), `queue-view.tsx` (`themeOf`, robot rows, send list), `register.tsx` (`prompt.submit`).

## Defects (in `defects\`)

1. `rivet-1-sent-card-loses-theme-on-other-spelling.md`: theme set before the robot's first card under another case is dropped from the sent card (`themes.get(card.robot)` matches exact spelling; assign matches cards only). Wrong result.
2. `rivet-2-plus-stays-armed-after-hint-cleared.md`: + on an empty box stays armed after any queue change wipes its hint (and with the queue switched off), so a later message to the chat is silently taken as a task. Wrong result. Worst for the person.
3. `rivet-3-plus-task-keeps-viewer-state-drops-files.md`: the task from + then send keeps the `<artifact-view-context>` block and loses pasted images; `set_steps` stores viewer state verbatim. Wrong result.
4. `rivet-4-multiline-card-splits-in-sent-message.md`: a multi-line card is sent as what reads like several cards with conflicting `done:` lines. Wrong result. Worst for send to another chat.
5. `rivet-5-send-delivers-then-fails-leaving-card-twice.md`: message delivered before archive and save; a failure after it leaves the card on both queues, and a retry sends it twice. Wrong result, rare trigger.
6. `rivet-6-set-theme-takes-empty-robot-and-multiline.md`: theme under an empty robot name; multi-line theme kept. Cosmetic.
7. `rivet-7-question-send-running-card.md`: question, whether sending the card being worked should be refused or warned (work goes on here, is filed again there, robot forgotten while running).

## What held

All the refusals the send_to_chat doc lists refuse with nothing sent or taken off; cards are sent in queue order, a repeated id once; a sent card asked for again is refused with when it was taken off; concurrent sends of one card deliver exactly once; robot spellings on cards are unified by assign; the band matches themes case-insensitively.

## Confusing

- The chats folder follows `CDD_CHATS_FOLDER`, not `CDD_HOME`: a tester or spec that sets only `CDD_HOME` writes into the person's real `~/.claude/cdd-chats` (and could deliver to a real chat's mailbox). The charter's rules name only `CDD_HOME`.
- Attachments of a sent card stay in the sending chat's attachments folder, named by path in the message; the receiving chat has no way to attach an existing path (`attach` takes base64), and the sending chat never deletes them, since `send_to_chat` archives without `_take_off`. Not reported as a defect: the doc says the files "stay where they are", but nothing ever cleans them and the receiving card holds no attachments.
- Receiving side is free text for an agent to parse and refile with five tools; whether cards land once depends on the agent, which nothing checks.

## Not reached

- The band itself: `prompt-queue.ts` imports `claude-code`, so no pure function I needed could run under tsx, and `register.test.tsx` needs the `claude` CLI, which this machine lacks. Defects 2, 3 and 7 are by reading, with exact code paths; the + then send plugin examples remain unrun anywhere.
- Robot rows' press area and drawing (not drawable without the plugin host).
- A cdd server on ports 18745-18749: not started; the tools were exercised through Python, which the server wraps.
- The receiving chat's refiling (needs a live agent).

## Remaining risk

+ then send (defects 2, 3) is the highest: it drops messages from the chat with no visible state, and it has no run test. Send to another chat relies on an agent parsing free text (defect 4) and on a non-atomic deliver-then-save (defect 5); a structured payload or an idempotency id per card would remove both risks.
