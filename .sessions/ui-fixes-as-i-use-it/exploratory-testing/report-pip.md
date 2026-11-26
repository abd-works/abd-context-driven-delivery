# Report — Pip, charter C1 (chat bar format chips and board sends)

Saved by the supervisor from Pip's answer; Pip's own write of this file was refused.

## Setup

A throwaway git project `sandbox\proj` (under `scratchpad\et\chips`) with the story map in markdown, draw.io and whiteboard, the class model in markdown and Python (`ordering/`), and a design canvas folder with `versions.json`. Sessions `chips-ticket` (stories, clean engineering and UX on) and `fresh` (stories only). Fake chats in `sandbox\no-chats`. The real tools were driven through `ProjectToolsets.of_repo(<worktree>)`; no server was started, so ports 18740-18744 went unused. Nothing was published or written outside the sandbox and the defect area.

## Tested

- The selection, toggle, `root_files`, the waiting read (`guidance_selection_after`, in one process and across processes), `choose_formats` and `choose_format`.
- Names that do not exist, capitalised spellings, empty names, an unknown part.
- A format pressed while its practice is off, and the last lit chip pressed off.
- Two toggles racing, in threads and in processes.
- `chat.send`, `check_in`, `confirm`, `resend` and `messages`: repeated presses, two senders at once, resend before confirm.
- `render.record_board` with odd addresses and paths.

## Defects

| File | Severity | What |
|---|---|---|
| `defects/pip-5-two-chat-sends-at-once-overwrite-one.md` | wrong result | Two `chat.send` calls at once get one file name from the clock; one message is lost and both report success. |
| `defects/pip-1-two-format-toggles-at-once-lose-one.md` | wrong result | Two format-chip toggles at once lose one press: the selection is worked out before `session.json` is held. |
| `defects/pip-6-board-link-any-text-sent-as-person.md` | wrong result | `record_board` takes any link text and rewrites `.whiteboard` files outside the project; Open sends that link as the person's message. |
| `defects/pip-4-chip-press-leaves-fidelity-no-format.md` | wrong result | Turning a lit chip off can save a fidelity with `"formats": []`. |
| `defects/pip-7-resend-while-taken-delivers-twice.md` | wrong result | `chat.resend` before the chat confirms delivers the message twice. |
| `defects/pip-2-toggle-guidance-accepts-unknown-names.md` | misleading message | `toggle_guidance` reports success for names that do not exist. |
| `defects/pip-3-question-code-chip-on-before-any-press.md` | question | Adding the Specification stage lights the code chip before any press, hiding markdown. |

## Held as promised

Single presses list the right files, published files stay listed, the waiting read wakes, unknown parts and fidelities are refused, `choose_formats` on a practice that is off works as documented, and `record_board` refuses a non-whiteboard or missing file.

## Confusing

- A chip is both a filter of the file list and the choice of formats a fidelity writes; every filter press rewrites `session.json`.
- Before any stage is chosen, `root_files` lists nothing unless the page's link names a fidelity.
- A practice turned off and on keeps its saved formats but the chips do not show them.
- Cosmetic, not filed: `choose_formats` with no fidelities says `"  offers no 'markdown' chip"`, with a blank where the fidelities should be.

## Not reached

- The chat bar's TypeScript (`guidance-client.ts` busy guard, `chat-turns.ts` `waitingSubmits`, `check-in-client.ts`): read, not run. It needs the `claude-code` runtime and `claude plugin test`; there is no `claude` CLI on this machine.
- The Files app page: Open was traced in code only.

## Still at risk

- Shared files read, changed and written without being held the whole time (pip-1, pip-5); there may be more such cases.
- The server queues every press as a new message; only `waitingSubmits` stops duplicates, and it empties when `$.prompt.submit` settles. If that settles when the prompt is queued rather than run, every press is delivered again. Not checked live.
- The one-second check-in has no guard against overlap, and a send may wait up to 3 s while the chat is busy.
- Text from a file reaches the chat as the person's own message (pip-6).
