# Question: sessions.switch to a name no session has makes a session folder and a card on the board

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Activate Ticket; the switch-session skill says "creating its folder when missing".
- **Module and class:** `space/session/open_sessions.py` `OpenSessions` (switch); `space/session/sessions.py`.
- **Severity:** answered question

## Steps
`sessions.switch name="no-such-session"` from a chat on `repo`; then `sessions.current`, `board.show`, `ls .sessions`.

## Expected
Unclear: a refusal naming the sessions there are, or a new session only when asked for one.

## Actual
The call answers the session's opening notes. `.sessions/no-such-session/` is made, committed on main ("sessions: no-such-session name no-such-session"), the board shows a card no-such-session In progress in Discovery, and `open-sessions.json` records the chat on it. A misspelled name makes a ticket nobody asked for.

## Tier that should catch it
Unit, once decided (`space/session/current_session_spec.py`).

## Also seen by

## Answer (2026-11-23)

sessions.switch to a name no session has is refused with UnknownSessionError, naming the sessions there are, unless create is passed, which makes it. Built in space/session/open_sessions.py and space/session/sessions.py (the switch-session docstring), every caller that makes a session passing create; tested by space/session/current_session_spec.py 'that a chat switches to a name no session has'; scenario "Refuse to switch a chat to a session nobody has" (under Activate Ticket) in story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md.
