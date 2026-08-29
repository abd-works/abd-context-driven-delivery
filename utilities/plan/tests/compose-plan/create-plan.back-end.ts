/**
 * Acceptance: Create Plan (back-end).
 * Sources: story-map.md Compose Plan / Create Plan; grill ticks 14–16
 */

import { story, scenario, expect } from "../../story-test";
import { Plan, Workflow, Workspace } from "../../domain/plan/plan";
import { freshWorld, ComposeWorld } from "./givens";

const world: ComposeWorld = freshWorld();

story("Create Plan", () => {
  scenario("Plan is Workflow plus tickets on the Workspace", ({ given, when, then }) => {
    given("a Workspace and a Workflow compose-judged-plan", () => {
      world.workspace = new Workspace();
      world.plan = null;
    });
    when("the operator creates a Plan from that Workflow with tickets 14 and 15", () => {
      const workflow = new Workflow("compose-judged-plan");
      world.plan = new Plan("compose-judged-plan", workflow);
      world.plan.setTickets([14, 15]);
      world.workspace.associate(world.plan);
    });
    then("that Plan is associated with that Workspace", () => {
      expect(world.workspace.plans).toContain(world.plan!);
      expect(world.plan?.workspace).toBe(world.workspace);
    })
      .and("that Plan is based on Workflow compose-judged-plan", () => {
        expect(world.plan?.workflowName).toBe("compose-judged-plan");
      })
      .and("that Plan names those tickets and holds no planned-turn list", () => {
        expect(world.plan?.tickets).toEqual([14, 15]);
        expect(world.plan?.turns.length).toBe(0);
      });
  });

  scenario("Second Plan is its own Plan", ({ given, when, then }) => {
    given("a Workspace that already has a Plan compose-judged-plan", () => {
      world.workspace = new Workspace();
      world.plan = new Plan("compose-judged-plan", new Workflow("compose-judged-plan"));
      world.plan.setTickets([14]);
      world.workspace.associate(world.plan);
    });
    when("the operator creates a Plan ticket-flow-plan with its own tickets", () => {
      world.secondPlan = new Plan("ticket-flow-plan", new Workflow("ticket-flow"));
      world.secondPlan.setTickets([20, 21]);
      world.workspace.associate(world.secondPlan);
    });
    then("that Workspace has both Plans", () => {
      expect(world.workspace.plans.length).toBe(2);
    }).and("each Plan holds its own tickets", () => {
      expect(world.plan?.tickets).toEqual([14]);
      expect(world.secondPlan?.tickets).toEqual([20, 21]);
    });
  });
});
