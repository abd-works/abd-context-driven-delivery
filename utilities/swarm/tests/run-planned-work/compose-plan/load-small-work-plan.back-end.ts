/**
 * Acceptance: Load Small-Work Plan (back-end).
 * Sources: story-map.md Compose Plan / Load Small-Work Plan; load-small-work-plan.md
 */

import { story, scenario, expect } from "../../story-test";
import { PlanCommands, Workspace } from "../../../domain/plan/plan";
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
      .and("that Plan holds the prebaked Turns from that Workflow", () => {
        expect(world.plan?.turns.length).toBe(2);
        expect(world.plan?.turns[0].context).toContain("root-cause");
        expect(world.plan?.turns[0].context).toContain("themed-defects");
      })
      .and("no GitHub issue was started", () => {
        expect(world.plan?.turns.every((t) => t.state === "Backlog")).toBe(true);
      });
  });

  scenario("Plan is based on a newly named Workflow", ({ given, when, then }) => {
    given("a Workspace working folder", () => {
      world.workspace = new Workspace();
      world.commands = new PlanCommands();
    });
    when("the operator runs /plan with workflow hotfix-batch and context login-bug", () => {
      world.plan = world.commands.plan(world.workspace, "hotfix-batch", "login-bug");
    });
    then("that Plan is based on Workflow hotfix-batch", () => {
      expect(world.plan?.workflowName).toBe("hotfix-batch");
    }).and("that Plan name is hotfix-batch", () => {
      expect(world.plan?.name).toBe("hotfix-batch");
    });
  });

  scenario("Small-work Turns do not inject CleanEngineering", ({ given, when, then }) => {
    given("a Plan loaded from Workflow small-work", () => {
      world.workspace = new Workspace();
      world.commands = new PlanCommands();
      world.plan = world.commands.smallWork(world.workspace, "themed-defects");
    });
    when("the operator reviews the Turn tool_keys", () => {
      /* observation only — tool_keys already on Turns */
    });
    then("the behavior Turn lists Bdd", () => {
      const keys = world.plan?.turns[0].toolKeys ?? [];
      expect(keys.some((k) => k.includes("Bdd"))).toBe(true);
    }).and("that Turn does not list CleanEngineering injected by Plan", () => {
      const keys = world.plan?.turns.flatMap((t) => t.toolKeys) ?? [];
      expect(keys.some((k) => k.includes("CleanEngineering"))).toBe(false);
    });
  });
});
