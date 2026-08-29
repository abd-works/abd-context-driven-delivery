/**
 * Acceptance: Start Ticket On Flow / Finish Plan / throwaway Workflow (back-end).
 * Sources: grill-answers.md ticks 21, 24, 29â€“33
 */

import { story, scenario, expect } from "../../story-test";
import { PlanCommands, Workflow, Workspace } from "../../domain/plan/plan";
import { freshWorld, ComposeWorld } from "./givens";

const world: ComposeWorld = freshWorld();

story("Start Ticket On Flow", () => {
  scenario("Named flow start puts the ticket on the flow and creates a Turn", ({ given, when, then }) => {
    given("a Plan on Workflow small-work", () => {
      Object.assign(world, freshWorld());
      world.plan = world.commands.smallWork(world.workspace, "themed", []);
      world.plan.workflow!.flowFile.configureState("Root Cause", {
        action: "Generate",
        tools: ["Bdd"],
      });
    });
    when("the operator runs /start-ticket /small-work 14", () => {
      world.turn = world.commands.startTicket(world.plan!, "small-work", 14);
    });
    then("ticket 14 is on that Plan", () => {
      expect(world.plan?.tickets).toContain(14);
    }).and("a Turn was created for the first flow state", () => {
      expect(world.turn?.ticketNumber).toBe(14);
      expect(world.turn?.state).toBe("In Progress");
      expect(world.plan?.turns.length).toBe(1);
    });
  });

  scenario("Unnamed start stays In Progress without a flow state", ({ given, when, then }) => {
    given("a Plan on Workflow small-work", () => {
      Object.assign(world, freshWorld());
      world.plan = world.commands.plan(world.workspace, "small-work", []);
    });
    when("the operator runs /start-ticket 14 without a flow name", () => {
      world.turn = world.commands.startTicket(world.plan!, "", 14);
    });
    then("ticket 14 is In Progress with no flow state", () => {
      expect(world.turn?.ticketNumber).toBe(14);
      expect(world.turn?.flowState).toBeNull();
      expect(world.turn?.state).toBe("In Progress");
    });
  });
});

story("Finish Plan", () => {
  scenario("/finish-plan clears plan tickets after flow-done", ({ given, when, then }) => {
    given("a Plan whose tickets finished the flow but remain listed", () => {
      Object.assign(world, freshWorld());
      world.plan = world.commands.plan(world.workspace, "small-work", [14, 15]);
      world.plan.enterState(14, "Done");
      world.plan.enterState(15, "Done");
    });
    when("the operator runs /finish-plan", () => {
      world.plan!.finishPlan();
    });
    then("that Plan is finished and holds no tickets", () => {
      expect(world.plan?.finished).toBe(true);
      expect(world.plan?.tickets.length).toBe(0);
    });
  });
});

story("Compose throwaway Workflow", () => {
  scenario("throwaway workflow is marked and cleared on finish", ({ given, when, then }) => {
    given("a throwaway Workflow tmp-theme on a Plan", () => {
      Object.assign(world, freshWorld());
      const workflow = new Workflow("tmp-theme");
      workflow.composethrowaway();
      world.plan = world.commands.plan(world.workspace, "tmp-theme", [14]);
      world.plan.workflow = workflow;
    });
    when("the operator finishes the Plan", () => {
      expect(world.plan!.workflow!.throwaway).toBe(true);
      world.plan!.finishPlan();
    });
    then("that Workflow remains throwaway for cleanup", () => {
      expect(world.plan!.workflow!.throwaway).toBe(true);
      expect(world.plan!.finished).toBe(true);
    });
  });

  scenario("Saved workflow is not throwaway after save", ({ given, when, then }) => {
    given("a Workflow hotfix-batch", () => {
      Object.assign(world, freshWorld());
      world.plan = world.commands.plan(world.workspace, "hotfix-batch", []);
    });
    when("the operator saves that Workflow to Project 7", () => {
      world.plan!.workflow!.save("acme", 7);
    });
    then("throwaway is false and project number is 7", () => {
      expect(world.plan!.workflow!.throwaway).toBe(false);
      expect(world.plan!.workflow!.projectNumber).toBe(7);
      expect(world.plan!.workflow!.flowFile.projectNumber).toBe(7);
    });
  });
});

