# draw-association-for-caller-not-only-owner

- **entry_id:** 803ffadf
- **artifact:** context_tools/actions/eval/.context/sessions/eval-consolidate-workspace/workspace-eval-oo-sketch.md
- **rule:** (process) draw-association-for-caller-not-only-owner
- **wrong:** Model conflated composition with CE associations — omitted Turn→GitRepo because Turn uses workSession.git without owning GitRepo; Relationships (target CE) initially said "No Turn→GitRepo" though Turn.finish calls commit/push and callers need association edges in the model separate from ownership.
- **status:** fixed
