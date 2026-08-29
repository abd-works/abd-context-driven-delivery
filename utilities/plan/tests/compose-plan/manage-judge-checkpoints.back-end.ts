/**
 * Acceptance: Manage Judge Checkpoints (back-end) — judge rubric on flow states.
 * Sources: grill-answers.md tick 28
 */

import { story, scenario, expect } from "../../story-test";
import {
  aWorkspaceWithWorkflow,
  freshWorld,
  ComposeWorld,
} from "./givens";

const world: ComposeWorld = freshWorld();

story("Manage Judge Checkpoints", () => {
  scenario("State rubric attaches JudgeCheckpoint on enter", ({ given, when, then }) => {
    given("flow file state Fix includes judge rubric small-work-fix", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "small-work");
      world.plan!.workflow!.flowFile.configureState("Fix", {
        judgeRubric: "small-work-fix",
      });
    });
    when("ticket 14 enters Fix", () => {
      world.turn = world.plan!.enterState(14, "Fix");
    });
    then("the created Turn has a JudgeCheckpoint against small-work-fix", () => {
      expect(world.turn?.judgeCheckpoint?.rubric).toBe("small-work-fix");
    });
  });

  scenario("No rubric means no judge on that state", ({ given, when, then }) => {
    given("state Root Cause has no judge rubric", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "small-work");
      world.plan!.workflow!.flowFile.configureState("Root Cause", {
        action: "Generate",
      });
    });
    when("ticket 14 enters Root Cause", () => {
      world.turn = world.plan!.enterState(14, "Root Cause");
    });
    then("the created Turn has no JudgeCheckpoint", () => {
      expect(world.turn?.judgeCheckpoint).toBeNull();
    });
  });
});
