---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Review Files In Files App

Map: [story-map.md](../../../.context/story-map.md#e-review-files-in-files-app). Acceptance tests: `tools/error_display/failure_spec.py` for what a failure answers (its kind's causes and its fix command); `harness/files_app/app/files/failure-fixes.spec.ts` for what only the page shows; `send-failure-to-be-fixed.story.ui_e2e_spec.py` beside this file for the page on its real server. The other scenarios of this epic are in [review_files_in_files_app_story.test.md](review_files_in_files_app_story.test.md).

### Domain terms

- failure: something a person ran that did not work, as a person sees it: what failed with the reason it gave, and the context it failed in (`tools/error_display/failure.py` *Failure*).
- failure kind: the kind of failure a page or an action met, which holds the causes that kind most often has, the likeliest first: a file that cannot be shown, a link to a file or heading that is not there, a graph view that fails, a render action that fails, a generate action that fails, session roots that are wrong or missing (*FailureKind*, `FAILURE_KINDS`).
- fix command: what Fix sends to the chat, the debug session command with the fix chosen and, as its details, the failure, its context and its kind's causes to check first (`Failure.fix_command`, `space/session` `debug_session`).
- failure band: the band under the Files page's head that keeps each failure the page met, with Fix and its dismiss, until a person dismisses it (`harness/files_app/app/files/failure-band-view.tsx`, `failure-fixes.ts` *FailureFixes*).

## Story: Send Failure To Be Fixed

Requested 2026-11-20, the person: "error in display or rendering / generation action or session roots --> fix button with most common causes listed to send to ai to fix".

#### Scenario: Send a file that cannot be shown to be fixed

*Given* the session of ticket bookshop lists `.context/thin-slice.md`, and the chat lens-chat opened the Files app on it
*And* `.context/thin-slice.md` was deleted on disk after the page listed it
*When* the Person opens `.context/thin-slice.md`
*Then* the failure band shows the failure with the context it failed in, opening `.context/thin-slice.md`, and a Fix button
*When* the Person asks for the failure to be fixed
*Then* the failure band lists the most common causes of a file that cannot be shown, the first that the file was moved, renamed or deleted after the page listed it
*And* the chat lens-chat is sent the fix command, whose details hold the failure, its context and each of those causes
*And* the failure band says the fix was sent

#### Scenario: Send links that lead nowhere to be fixed

*Given* the story map `.context/story-map.md` of ticket bookshop links to `returns-policy.md`, which is not there
*When* the Person opens `.context/story-map.md`
*Then* the failure band shows that `.context/story-map.md` has a link that leads nowhere, `.context/returns-policy.md` is not there, with a Fix button
*When* the Person asks for the failure to be fixed
*Then* the failure band lists the most common causes of a link to a file or heading that is not there
*And* the chat lens-chat is sent the fix command with those causes

#### Scenario: Show the causes on a page no chat opened

*Given* the Files app is opened by no chat on the files of a session that is not there, so the files did not list
*When* the Person asks for the failure to be fixed
*Then* the failure band lists the most common causes of session roots that are wrong or missing
*And* it shows the fix command and says to copy it into a chat, since no chat opened the page
*And* nothing is sent

#### Scenario: Say why a fix did not reach the chat

*Given* the chat that opened the Files app is no longer connected
*When* the Person asks for a failure to be fixed
*Then* the failure band lists the causes and says the fix did not reach the chat, with the reason the chat gave
*And* the Person can ask for the fix again

#### Scenario: Dismiss a failure

*Given* the failure band shows a failure
*When* the Person dismisses it
*Then* the failure band no longer shows it
*And* reading the same file again does not bring it back

#### Scenario: Refuse a kind no failure has

*Given* the failure kinds are a file that cannot be shown, a missing link, a graph view, a render, a generate and the session's roots
*When* a failure is described with the kind weather
*Then* the failure is refused, naming weather and the kinds there are
*But* a failure described with no kind lists no causes, and its fix command still holds the failure and its context
