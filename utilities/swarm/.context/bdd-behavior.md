---
fidelity: [behavior]
artifact: [bdd]
format: md
---

# BDD — Execute themed tickets on a configured Plan Workflow

**Sources / context:** `utilities/swarm/.context/thin-slicing.md`; `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/workflow/.context/module-context.md`; `context_tools/bdd/bdd.md`; `utilities/plan/.context/module-context.md`

Increment 1 spine: preconfigured Plan as project Workflow; themed defects/small changes; root cause; `/bdd` with Clean Engineering under the hood; one fix; ticket Backlog → In Progress → Done.

---

Fidelity: behavior

a preconfigured Plan used as a project Workflow
  -> plan = Plan.create(workspace, name="themed-defects")
  -> workflow = new Workflow()

  that already holds configured Turns
    with tool_keys Bdd and CleanEngineering on the BDD Turn
      it should be ready to start without Compose
        -> expect(plan.turns).not_to be empty
        -> expect(plan.turns[0].tool_keys).to equal ["context_tools.bdd.bdd:Bdd", "context_tools.clean_engineering.clean_engineering:CleanEngineering"]

  that is started for a themed ticket
    with Workflow start moving the GitHub ticket to In Progress
      it should open a WorkSession and move the first Backlog Turn to In Progress
        -> session = plan.start()
        -> workflow.start(ticket="#23")
        -> expect(session.open_turn.state.name).to equal "In Progress"
        -> expect(ticket.state.name).to equal "In Progress"

a themed defect ticket under one common theme
  -> ticket = repo.ticket("#23")

  that has root cause recorded
    with a flow note on the Ticket
      it should keep the root cause on that Ticket
        -> repo.note(ticket, "root cause: missing CE companion on /bdd")
        -> expect(repo.read_notes(ticket)).to include("root cause: missing CE companion on /bdd")

  that runs /bdd for one issue
    with Clean Engineering under the hood on the same Turn
      it should invoke Bdd and its CleanEngineering companion together
        -> bdd = new Bdd(fidelity="behavior")
        -> ce = bdd.ce()
        -> plan.execute_turn()
        -> expect(turn.tool_keys).to include("context_tools.bdd.bdd:Bdd")
        -> expect(turn.tool_keys).to include("context_tools.clean_engineering.clean_engineering:CleanEngineering")
        -> expect(ce).to be_a(CleanEngineering)
      it should not run Bdd without CleanEngineering
        -> expect(turn.tool_keys).not_to equal ["context_tools.bdd.bdd:Bdd"]

  that fixes one issue at a time
    with Mistake and Correction on the Turn
      it should hold a new result and stay In Progress until advance
        -> plan.fix_and_rerun(mistake="bdd alone", correction="bdd+ce companion")
        -> expect(turn.result).not_to be empty
        -> expect(turn.state.name).to equal "In Progress"

  that is finished through Workflow
    with the issue Done and closed
      it should move the Ticket to Done via Workflow finish
        -> plan.advance_turn()
        -> workflow.finish(outcome="fixed themed defect")
        -> expect(ticket.state.name).to equal "Done"

a Practitioner reviewing themed Workflow progress
  that reviews after Judge and HIL
    it should show Turn result, HIL validation, and JudgeResult on the Plan
      -> progress = PlanExecution(plan).review_progress()
      -> expect(progress.result).not_to be none
