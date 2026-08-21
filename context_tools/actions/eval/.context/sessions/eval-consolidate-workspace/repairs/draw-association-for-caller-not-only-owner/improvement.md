# draw-association-for-caller-not-only-owner

- **tool:** CleanEngineering
- **error:** Model conflated composition with CE associations — omitted Turn→GitRepo because Turn uses workSession.git without owning GitRepo; Relationships (target CE) initially said "No Turn→GitRepo" though Turn.finish calls commit/push and callers need association edges in the model separate from ownership.
- **rule:** (process) draw-association-for-caller-not-only-owner
- **how:** Updated workspace-eval-oo-sketch.md Relationships and git caller table — added Turn→GitRepo association via workSession.git; clarified caller vs composition edges.
