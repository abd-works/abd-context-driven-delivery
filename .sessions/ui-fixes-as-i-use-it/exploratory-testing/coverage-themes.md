# Coverage themes — ui-fixes-as-i-use-it hardening

Scope: what branch `ui-fixes-as-i-use-it` changed since `main` (54+ commits) and what those changes can affect. The person named the areas on card 7651c123c132: the chat bar format chips and board sends; the queue band (robot rows, themes, + then send, send to another chat); the Files app right-click menu and All files; draw.io and whiteboard links and arrows; the story explorer class cards and realizations; the scenario reader; the class-card language. **Confirmed by the person:** the card that started this hardening (queue card 7651c123c132, 2026-11-26) names these seven areas as what hardening covers; they are taken as the person's themes, grouped into four by the code they run through. No theme was added beyond them. Everything else in the product is out of scope.

Counts are scenario files (md), story tests in code (story), board UI specs (ui), heavy and e2e specs, per sub-epic under `story_tests/`, plus the module specs behind each area.

## T1 — Chat bar format chips and board sends

- **Change behind it:** 778866be2 (chip takes a press anywhere), 48b156f34 (busy chip, second press waits), a11a6a51f (board send waits for the chat's turn, no second copy).
- **Evidence:** `.sessions/_backlog/chat-ui-defects.md` — three defects this week in the chat bar (dead chips, silent filter, board send copied per press). Each fix says "No mod test: the mod harness does not run from a shell" or "format-chip-busy.test.ts, not run". `claude` CLI is still absent on this machine, so `claude plugin test` cannot run. `story_tests/move-work-forward-from-chat-bar/*`: 10 sub-epics, 1 md each, 0 story tests, 0 ui, 2 heavy (integrate-practice-content-editor-apps only), 0 e2e. The Python under the chips (`session.toggle_guidance`, format filter via `session.folder_files`) and under board send (`chat.send`, `render.record_board`) is what a tester can run for real.
- **Risk:** a chip toggle that answers with the wrong selection or a stale list; two toggles at once; a board send queued twice by the server side.

## T2 — Queue band: robot rows, themes, + then send, send to another chat

- **Change behind it:** 84507b659, a3b503bad (row takes the press), 57eaf5bca (robot theme), a37bd1d13 (+ then the next message is the card's task), 019bbd4a4 (send cards to another chat).
- **Evidence:** chat-ui-defects.md entries for each: "plugin tests in register.test.tsx, not run: no claude CLI on this machine", "Not seen live". `story_tests/queue-prompts-for-later`: 7 sub-epics, 4 story tests in all, 0 ui, 0 e2e; `tools/prompt_queue` has 115 unit, 22 heavy, 8 plugin e2e examples. `prompt-queue.send_to_chat` and `set_theme` are new tools with only unit coverage; send_to_chat really writes another chat's mailbox.
- **Risk:** cards lost or duplicated when sent to another chat (refusal paths, partial failure), theme matched to the wrong robot spelling, + on an empty box swallowing a message it should not.

## T3 — Files app right-click menu and All files

- **Change behind it:** acbb7d184 (menu: delete after confirming, validate, violations, add to practice), 3af6f1b48 (`session.delete_file`), e89ed3407 / 80993e5a9 / 1eeff85a4 (All files), 8c9596efb (`add_root`), 32ec08e1b (published canvas name), 95afbb875 (e2e twin).
- **Evidence:** `story_tests/review-generated-work-in-file-viewer`: 9 sub-epics with an e2e each, but the file menu e2e covers the happy path only; `session.delete_file` deletes for real and refuses a root, its record and `.git` — unit spec only for refusals on odd paths (relative, `..`, symlink, a file outside every root). Files app has 23 vitest specs; the server is started only from the e2e.
- **Risk:** delete reaching outside the session's roots; All files listing ignored or duplicate files; add-to-practice on a file already a root.

## T4 — Diagrams, story explorer and the scenario reader

- **Change behind it:** draw.io/whiteboard links and arrows (6ab5a3cda, bc97a2c27, f0230fd74, e023a22d3, 4533f28e5, dac88ec09, 708e61efe, 861b06cfa, c53ca7f06, 5ada42896, 61ce521ba); story explorer class cards and realizations (9a3cd7d28, 1fc174754, 8302866bb, 200f27bf6, 3ad27a6c0); scenario reader (9b28b40ec, c9c92e932 and Sparky's follow-up); class-card language (0b24d7434, 49c17ee31, d9bd77f69).
- **Evidence:** chat-ui-defects.md: story map links in the draw.io viewer showed "not found" (fixed, "not seen live"). The scenario reader changed three times this week, each after a defect found on pml-web's layout (fff2264c825f, 9fb1b3e76773, 66d5c901eeec). `story_tests/draw-practice-models-on-claude-whiteboard`: 1 md, 0 tests of any tier; `story_tests/explore-stories-in-story-ui`: 4 sub-epics, 0 tests of any tier (explorer covered by module specs `story_explorer_heavy_spec.py`, `choose_lines_explorer_spec.py`).
- **Risk:** links that resolve on one layout and not another (file in a sub-folder, a heading with punctuation, a file renamed after render); arrows overlapping on a big model; a class card whose language loses paragraphs or bullets in round trip; scenarios dropped or duplicated when markdown and code disagree on a name.
