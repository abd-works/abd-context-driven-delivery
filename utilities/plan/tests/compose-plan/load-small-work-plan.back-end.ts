/**
 * Acceptance: Load Small-Work Plan (back-end).
 * Sources: story-map.md; grill ticks 14, 22–24
 */

import { story, scenario, expect } from "../../story-test";
import { PlanCommands, Workspace } from "../../domain/plan/plan";
import { freshWorld, ComposeWorld } from "./givens";

const world: ComposeWorld = freshWorld();

story("Load Small-Work Plan", () => {
  scenario("/plan /small-work loads the prebaked Workflow", ({ given, when, then }) => {
    given("a Workspace working folder", () => {
      world.workspace = new Workspace();
      world.commands = new PlanCommands();
      world.plan = null;
    });
    when("the operator runs /plan /small-work with context themed-defects", () => {
      world.plan = world.commands.smallWork(world.workspace, "themed-defects");
    });
    then("that Plan is based on Workflow small-work", () => {
      expect(world.plan?.workflowName).toBe("small-work");
      expect(world.plan?.workflow?.name).toBe("small-work");
    })
      .and("that Plan uses flow-file state behavior (no planned-turn list)", () => {
        expect(world.plan?.turns.length).toBe(0);
        expect(world.plan?.workflow?.flowFile.states.length).toBe(2);
        expect(world.plan?.workflow?.flowFile.states[0].prose).toContain("themed-defects");
      })
      .and("no GitHub issue was started", () => {
        expect(world.plan?.tickets.length).toBe(0);
      });
  });

  scenario("Plan is based on a newly named Workflow", ({ given, when, then }) => {
    given("a Workspace working folder", () => {
      world.workspace = new Workspace();
      world.commands = new PlanCommands();
    });
    when("the operator runs /plan with workflow hotfix-batch and tickets", () => {
      world.plan = world.commands.plan(world.workspace, "hotfix-batch", [42]);
    });
    then("that Plan is based on Workflow hotfix-batch", () => {
      expect(world.plan?.workflowName).toBe("hotfix-batch");
    }).and("that Plan name is hotfix-batch with those tickets", () => {
      expect(world.plan?.name).toBe("hotfix-batch");
      expect(world.plan?.tickets).toEqual([42]);
    });
  });

  scenario("Small-work state behavior does not inject CleanEngineering", ({ given, when, then }) => {
    given("a Plan loaded from Workflow small-work", () => {
      world.workspace = new Workspace();
      world.commands = new PlanCommands();
      world.plan = world.commands.smallWork(world.workspace, "themed-defects");
    });
    when("the operator reviews Fix state tool keys in the flow file", () => {
      /* observation */
    });
    then("the Fix state lists Bdd", () => {
      const fix = world.plan?.workflow?.flowFile.states.find((s) => s.name === "Fix");
      expect(fix?.tools.some((t) => t.includes("Bdd") || t.includes("bdd"))).toBe(true);
    }).and("Plan does not inject CleanEngineering", () => {
      const allTools = world.plan!.workflow!.flowFile.states.flatMap((s) => s.tools);
      expect(allTools.some((t) => t.toLowerCase().includes("clean"))).toBe(false);
    });
  });
});
