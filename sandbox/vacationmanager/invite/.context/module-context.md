# invite

- **Purpose:** Owns the Invite aggregate — models the lifecycle of adding a co-traveller to a vacation. Enforces that an invite is always scoped to a known vacation, tracks each invitee's response (pending → accepted / declined), and allows the organiser to remove a traveller. Read access to the traveller list flows through this module; the `vacation` module holds no traveller state.

- **Seam (terms):** `Invite`, `InviteId`, `Traveller`, `InviteResponse`

- **Dependencies (one-way):** `vacation` (`VacationId`)
