# Chat UI defects

Each defect a person reported in the chat UI, and where it stands. The earlier list, all fixed, is in `.sessions/_complete/chat-ui-defects/chat-ui-defects.md`.

## The queue band shows a pasted message as the goal's title, with 77 interruptions under it

Reported 2026-11-23. The queue band read "70/77 1. [interruption] <pasted_content id="7250"> ## Notes from the backlog From `board-enhancements…`". The person's first message of the chat was pasted text, so the goal took the raw paste, tags included, as its title. Then every later message, whatever it was about, was filed under that goal as an `[interruption]` step, until it held 77 steps; the main chat had to rename it and mark it done by hand.

Wanted: a goal's title is a short summary of what it asks, never raw pasted text or its `<pasted_content>` tags. A message about new work starts a goal of its own instead of becoming another step of the last one. A goal holding many unrelated interruptions is split, or its finished steps folded away.

Fixed 2026-11-23 on `release-1-2-fixes`. A goal's title is now the first sentence of the person's own words, with any `<pasted_content>` paste and its tags taken out, or the paste's first line when the message is only a paste, cut at a word to 80 characters (`goalTitleOf` in `tools/prompt_queue/hooks/queue/goal-title.ts`). The prompt.submit hook files a message under the goal last worked only while a turn works that goal or when its turn ended asking the person something; any other message sent between turns starts a goal of its own. Tested in `tools/prompt_queue/hooks/register.test.tsx` and `prompt_queue_plugin_e2e_spec.py`; scenarios in Queue Sent Prompt As Running and Add Interruption To Working Prompt. Built 2026-11-24, also on `release-1-2-fixes`: a goal that gathered interruptions is split by the cdd server (`prompt-queue.split`, and ⑂ among the card's buttons while it holds an interruption still to do): each interruption not done becomes a card of its own right after the goal, given the goal's robot, and the goal keeps its own steps and the interruptions already done. Once a card holds three or more finished steps, they fold into one line under it, "▸ ✓ 3 done", which shows them again when pressed. Tested in `prompt_queue_spec.py`, `prompt_queue_heavy_spec.py` and `register.test.tsx`; scenarios in Show Prompt Steps In Queue and the new Split Goal Of Interruptions. Not yet seen in the live band.

## The chat bar's format chips do nothing, or answer only after several presses

Reported 2026-11-26 from pml-web built features. The orange format chips (◇ diagram, M↓ markdown, </> code, ▦ canvas) seemed dead or very slow.

Cause: the see-through Button `GlyphButtonView` lays over a glyph was one blank wide, so only the glyph's first cell took a press; the chip's orange padding and the rest of `</>` and `M↓` did nothing. The server's toggle answers in about a second.

Fixed 2026-11-26 on `ui-fixes-as-i-use-it` (778866be2): the Button is one blank per character of the glyph, and the chip's padding is part of its glyph, so the whole chip takes the press. No mod test: the mod harness does not run from a shell. Not yet seen in the live bar.

## A board send says "Board sent" but reaches the chat only when its turn ends, every press as another copy

Reported 2026-11-26 from pml-web built features. Pressing Open on a published whiteboard in the Files app toasted "Board sent: Open the whiteboard … in the artifact panel", but the chat, mid-turn, saw nothing until its turn ended; then all four presses arrived together as one message.

Cause: Claude Code runs a plugin's `$.prompt.submit` only once the chat is idle (its `wait` is false: "a plugin's prompt runs once idle"); only a peer's message or a notification reaches a running turn, so a board send cannot open the artifact mid-turn. It always worked so; it seemed instant only when the chat was idle. The toast said "sent" at press time, and every press was submitted again.

Fixed 2026-11-26 on `ui-fixes-as-i-use-it`: while the chat works, the toast says the board message waits for the chat to finish its turn; a send whose text already waits is not submitted again (`waitingSubmits` in `board-chat/chat-turns.ts`, cleared when a turn starts), and its toast says it already waits. The Files app's toast says the chat opens it when its turn ends. No mod test; not yet seen in the live bar.

## The Files app names a design canvas by its version folder, not the title it is published under

Reported 2026-11-26 from pml-web built features. pml-web's canvas at `ux/design-canvas/version-7/project/canvas.json` showed as "version-7 ↗ design canvas", while it is published as "ux-mockup" (kept as one, `keep_one` in versions.json).

Fixed 2026-11-26 on `ui-fixes-as-i-use-it`: `publication_of` gives the canvas's title (`CanvasVersion.title`: `ux-mockup` kept as one, `ux-mockup.version-N` while versions are kept) as the Publication's name, `FileEntry.published_name` sends it, and the file bar shows it, the version folder only when none is sent. Tested in `space/session/practices/publication_spec.py` and `file-bar.spec.ts`. Left: a scoped canvas is titled from the unscoped name (`ux-mockup`, not `{scope}-ux-mockup`), since the path does not say its scope, as `publication_of` already read it. Not yet seen in the live Files app.

## A story map link opened in the draw.io viewer shows "not found"

Reported 2026-11-26. A story's link in `.context/story-map.drawio`, opened in the draw.io viewer, went to `127.0.0.1:8791/story_tests/...` and showed "not found": the links are written beside the diagram, and the browser read them against the viewer, which serves only diagrams.

Fixed 2026-11-26 on `ui-fixes-as-i-use-it` (6ab5a3cda, bc97a2c27): the viewer sends each link to a file through the Files server's `/api/drawio/link`, which opens the file in the Files app at the heading its anchor names, and writes the links back as they were on save; a link to a file that is not there is told to the chat, whose chat bar offers Fix. Tested in `tools/drawio_viewer/drawio_viewer_spec.py` and `drawio-link.spec.ts`. Not yet seen live: the Files app and viewer running now are the stable lane's.

## A format chip's filter shows nothing while it runs

Reported 2026-11-26 from pml-web. A press on a format chip, in "all" mode above all, took a while to filter and nothing said it was working, so a second press was easy.

Fixed 2026-11-26 on `ui-fixes-as-i-use-it`: on the chat bar the pressed chip shows the busy wheel and the bar says "filtering by markdown…" until the answer lands, and a press while one runs starts nothing (`pressedGuidance` in `guidance-client.ts`; `format-chip-busy.test.ts`, not run: the mod harness does not run from a shell). The Files app says "Filtering by …" in place of the list until it is read again, and ignores a press while one filters (`files-page.spec.ts`). The slowness itself, the graph rebuilt on each change, is a separate item.

## A robot's row in the queue band takes a click only on a narrow strip

Reported 2026-11-26. In sub-agent mode, the robot rows ("Sparky 0/1") opened their queue only when the click landed on the robot picture's first cell: the see-through Button over it was one blank wide.

Fixed 2026-11-26 on `ui-fixes-as-i-use-it`: the Button lies over the whole row, robot, name and count, one blank per column (`AgentRobotView` in `tools/prompt_queue/hooks/queue/queue-view.tsx`). The tests press it by its key, unchanged. Not seen live: not repinned while the person demos pml-web on the dev lane.

## + on a card with an empty prompt box: the task sent next went to the chat

Reported 2026-11-26. A card's + ("Add task") pressed with the prompt box empty said "Type the task in the prompt box, then press + to add it." The person typed the task and sent it with Enter, expecting it to become the card's task; it went to the chat as an ordinary prompt.

Fixed 2026-11-26 on `ui-fixes-as-i-use-it`: + on an empty prompt box waits on that card, and the next message sent (not a slash command, not the mod's own) becomes the card's last task, not started, through the same `set_steps` call + uses, and never reaches the chat ("Added as a task"); the hint clears and the message after it goes to the chat as usual. The hint now reads "Type the task in the prompt box and send it, or press + again, to add it to this card." (`addStep` and `takeAwaitedStep` in `tools/prompt_queue/hooks/queue/prompt-queue.ts`, the `prompt.submit` hook in `register.tsx`; plugin tests in `register.test.tsx`, not run: no `claude` CLI on this machine). Not seen live: not repinned while the person demos pml-web on the dev lane. Whether the desktop leaves the sent text in the prompt box after the drop is not checked.
