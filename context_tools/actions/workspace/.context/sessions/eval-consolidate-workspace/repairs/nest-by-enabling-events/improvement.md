# nest-by-enabling-events

- **tool:** Bdd
- **error:** Used operation outcomes as nested states: `that has logged its action run` and `that has expanded its action instructions`. Logging is not a standing state — the `that` must name what triggers the record (agent asks for instructions → expansion trail; recipe body runs → run trail). Same class of error as treating API steps as subjects.
- **rule:** nest-by-enabling-events
- **how:** Nest under turn finish for action-run audit; expand under that is asked for its instructions.
