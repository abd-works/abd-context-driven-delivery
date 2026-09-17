/**
 * Acceptance: Create Plan (back-end).
 * Sources: story-map.md Compose Plan / Create Plan; create-plan.md
 */

import { story, scenario, expect } from "../../story-test";
import { Plan, Workflow, Workspace } from "../../domain/plan/plan";
import { freshWorld, ComposeWorld } from "./givens";

const world: ComposeWorld = freshWorld();

story("Create Plan", () => {
  scenario("Plan is on the Workspace based on a Workflow", ({ given, when, then }) => {
    given("a Workspace and a Workflow compose-judged-plan", () => {
      world.workspace = new Workspace();
      world.plan = null;
    });
    when("the operator creates a Plan from that Workflow", () => {
      const workflow = new Workflow("compose-judged-plan");
      world.plan = new Plan("compose-judged-plan", workflow);
      world.workspace.associate(world.plan);
    });
    then("that Plan is associated with that Workspace", () => {
      expect(world.workspace.plans).toContain(world.plan!);
      expect(world.plan?.workspace).toBe(world.workspace);
    }).and("that Plan is based on Workflow compose-judged-plan", () => {
      expect(world.plan?.workflowName).toBe("compose-judged-plan");
    });
  });

  scenario("Second Plan is its own Plan", ({ given, when, then }) => {
    given("a Workspace that already has a Plan compose-judged-plan", () => {
      world.workspace = new Workspace();
      world.plan = new Plan("compose-judged-plan", new Workflow("compose-judged-plan"));
      world.workspace.associate(world.plan);
      world.plan.addTurn({ action: "generate", fidelity: "story_map" });
    });
    when("the operator creates a Plan ticket-flow-plan based on a Workflow", () => {
      world.secondPlan = new Plan("ticket-flow-plan", new Workflow("ticket-flow"));
      world.workspace.associate(world.secondPlan);
      world.secondPlan.addTurn({ action: "generate", fidelity: "scenarios" });
    });
    then("that Workspace has both Plans", () => {
      expect(world.workspace.plans.length).toBe(2);
    }).and("each Plan holds its own Turns", () => {
      expect(world.plan?.turns.length).toBe(1);
      expect(world.secondPlan?.turns.length).toBe(1);
      expect(world.plan?.turns[0]).not.toBe(world.secondPlan?.turns[0]);
    });
  });
});
