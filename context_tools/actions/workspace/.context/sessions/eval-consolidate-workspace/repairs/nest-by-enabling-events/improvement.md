# nest-by-enabling-events

- **tool:** Bdd
- **error:** Nested commit under `with a dirty working tree on its session branch` at turn finish. Finishing a turn after work always commits scoped changes — dirty is not an optional `with` branch.
- **rule:** nest-by-enabling-events
- **how:** Remove dirty `with`; commit is direct outcome under that has finished its turn.
