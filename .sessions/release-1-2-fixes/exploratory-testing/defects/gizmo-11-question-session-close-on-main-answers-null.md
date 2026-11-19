# Question: session.close on main answers null with no refusal, while ticket.close on main refuses

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Close Active Session.
- **Module and class:** `space/session/session.py` `Session.close`; compare `space/kanban/ticket.py` `Ticket._refuse_main`.
- **Severity:** question

## Steps
`session.close session=".sessions/main/session.json"`; then `ticket.close ticket="main"`.

## Expected
One answer for both: `MainStaysOpenError: main is the default session and stays open; it cannot close`.

## Actual
`session.close` answers `null` and nothing changes; `ticket.close` raises MainStaysOpenError. A caller of `session.close` cannot tell that nothing was closed.

## Tier that should catch it
Unit (`space/session/session_spec.py`).

## Also seen by
