/**
 * Acceptance: Manage HIL Checks (back-end).
 * Sources: plan-and-swarm-sketch.md; manage-hil-checks.md
 */

import { story, scenario, expect } from "../../story-test";
import { HILCheck } from "../../../domain/plan/plan";
import {
  aPlanWithGenerateTurn,
  aWorkspaceWithWorkflow,
  freshWorld,
  ComposeWorld,
} from "./givens";

const world: ComposeWorld = freshWorld();

story("Manage HIL Checks", () => {
  scenario("Add a HIL Check", ({ given, when, then }) => {
    given("a Plan with a Turn Stories generate story_map", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
    });
    when("the operator adds a HILCheck to that Turn", () => {
      world.attachments.addHil(world.turn!, new HILCheck("confirm sketch"));
    });
    then("that Turn has the HILCheck", () => {
      expect(world.turn?.hilCheck).not.toBeNull();
      expect(world.turn?.hilCheck?.validation).toBe("confirm sketch");
    }).and("the Plan still has that one Turn", () => {
      expect(world.plan?.turns.length).toBe(1);
    });
  });

  scenario("Edit a HIL Check", ({ given, when, then }) => {
    given("a Turn that already has a HILCheck", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
      world.attachments.addHil(world.turn!, new HILCheck("old"));
    });
    when("the operator edits that HILCheck", () => {
      world.attachments.editHil(world.turn!, new HILCheck("updated"));
    });
    then("that Turn still has one HILCheck", () => {
      expect(world.turn?.hilCheck?.validation).toBe("updated");
    });
  });

  scenario("Delete a HIL Check", ({ given, when, then }) => {
    given("a Turn that already has a HILCheck", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
      world.attachments.addHil(world.turn!);
    });
    when("the operator deletes that HILCheck", () => {
      world.attachments.deleteHil(world.turn!);
    });
    then("that Turn has no HILCheck", () => {
      expect(world.turn?.hilCheck).toBeNull();
    });
  });

  scenario("HIL Check stays when a Judge Checkpoint is added", ({ given, when, then }) => {
    given("a Turn that already has a HILCheck", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
      world.attachments.addHil(world.turn!, new HILCheck("keep-me"));
    });
    when("the operator adds a JudgeCheckpoint against rubric stories-scenarios", () => {
      world.attachments.addJudge(world.turn!, "stories-scenarios");
    });
    then("that Turn has the HILCheck", () => {
      expect(world.turn?.hilCheck?.validation).toBe("keep-me");
    }).and("that Turn has the JudgeCheckpoint", () => {
      expect(world.turn?.judgeCheckpoint?.rubric).toBe("stories-scenarios");
    });
  });
});
