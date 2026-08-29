/**
 * Acceptance: Manage HIL Checks (back-end) — hil marks on flow states.
 * Sources: grill-answers.md ticks 26–27
 */

import { story, scenario, expect } from "../../story-test";
import { HILCheck } from "../../domain/plan/plan";
import {
  aWorkspaceWithWorkflow,
  freshWorld,
  ComposeWorld,
} from "./givens";

const world: ComposeWorld = freshWorld();

story("Manage HIL Checks", () => {
  scenario("Marking a state hil attaches HILCheck when entered", ({ given, when, then }) => {
    given("flow file marks state Review with hil", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "small-work");
      world.plan!.workflow!.flowFile.configureState("Review", {
        hil: true,
        prose: "confirm the fix",
      });
    });
    when("ticket 14 enters Review", () => {
      world.turn = world.plan!.enterState(14, "Review");
    });
    then("the created Turn has a HILCheck", () => {
      expect(world.turn?.hilCheck).not.toBeNull();
      expect(world.turn?.hilCheck?.prompt).toBe("confirm the fix");
    });
  });

  scenario("Clearing hil on a state removes future HILChecks", ({ given, when, then }) => {
    given("state Review was marked hil then cleared", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "small-work");
      world.plan!.workflow!.flowFile.configureState("Review", { hil: true });
      world.plan!.workflow!.flowFile.configureState("Review", { hil: false, prose: null });
    });
    when("ticket 14 enters Review", () => {
      world.turn = world.plan!.enterState(14, "Review");
    });
    then("that Turn has no HILCheck", () => {
      expect(world.turn?.hilCheck).toBeNull();
    });
  });

  scenario("Attachments can still edit HILCheck on a live Turn", ({ given, when, then }) => {
    given("a Turn that already has a HILCheck", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "small-work");
      world.plan!.workflow!.flowFile.configureState("Review", { hil: true, prose: "old" });
      world.turn = world.plan!.enterState(14, "Review");
    });
    when("the operator edits that HILCheck", () => {
      world.attachments.editHil(world.turn!, new HILCheck("new prompt"));
    });
    then("that Turn still has one HILCheck with the new prompt", () => {
      expect(world.turn?.hilCheck?.prompt).toBe("new prompt");
    });
  });
});
