/**
 * Acceptance: Manage Judge Checkpoints (back-end).
 * Sources: plan-and-swarm-sketch.md; manage-judge-checkpoints.md
 */

import { story, scenario, expect } from "../../story-test";
import { HILCheck, ToolCall } from "../../domain/plan/plan";
import {
  aPlanWithGenerateTurn,
  aWorkspaceWithWorkflow,
  freshWorld,
  ComposeWorld,
} from "./givens";

const world: ComposeWorld = freshWorld();

story("Manage Judge Checkpoints", () => {
  scenario("Add a Judge Checkpoint", ({ given, when, then }) => {
    given("a Plan with a Turn Stories generate story_map", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
    });
    when("the operator adds a JudgeCheckpoint against rubric stories-scenarios", () => {
      world.attachments.addJudge(world.turn!, "stories-scenarios");
    });
    then("that Turn has the JudgeCheckpoint", () => {
      expect(world.turn?.judgeCheckpoint).not.toBeNull();
    })
      .and("that JudgeCheckpoint rubric is stories-scenarios", () => {
        expect(world.turn?.judgeCheckpoint?.rubric).toBe("stories-scenarios");
      })
      .and("the Plan still has that one Turn", () => {
        expect(world.plan?.turns.length).toBe(1);
      });
  });

  scenario("Later Turn can have its own Judge Checkpoint", ({ given, when, then }) => {
    given("a Turn that already has JudgeCheckpoint stories-scenarios and a later Turn", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
      world.attachments.addJudge(world.turn!, "stories-scenarios");
      world.plan!.addTurn({
        action: "generate",
        fidelity: "modules",
        toolKeys: ["CleanEngineering"],
        toolCalls: [new ToolCall("CleanEngineering", "generate")],
      });
    });
    when("the operator adds a JudgeCheckpoint to the later Turn against rubric plan-modules", () => {
      const later = world.plan!.turns[1];
      world.attachments.addJudge(later, "plan-modules");
    });
    then("the first Turn still has stories-scenarios", () => {
      expect(world.plan?.turns[0].judgeCheckpoint?.rubric).toBe("stories-scenarios");
    }).and("the later Turn has plan-modules", () => {
      expect(world.plan?.turns[1].judgeCheckpoint?.rubric).toBe("plan-modules");
    });
  });

  scenario("Edit a Judge Checkpoint", ({ given, when, then }) => {
    given("a Turn with JudgeCheckpoint stories-scenarios", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
      world.attachments.addJudge(world.turn!, "stories-scenarios");
    });
    when("the operator edits that JudgeCheckpoint rubric to stories-validate", () => {
      world.attachments.editJudge(world.turn!, "stories-validate");
    });
    then("that Turn JudgeCheckpoint rubric is stories-validate", () => {
      expect(world.turn?.judgeCheckpoint?.rubric).toBe("stories-validate");
    });
  });

  scenario("Delete a Judge Checkpoint", ({ given, when, then }) => {
    given("a Turn with a JudgeCheckpoint", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
      world.attachments.addJudge(world.turn!, "stories-scenarios");
    });
    when("the operator deletes that JudgeCheckpoint", () => {
      world.attachments.deleteJudge(world.turn!);
    });
    then("that Turn has no JudgeCheckpoint", () => {
      expect(world.turn?.judgeCheckpoint).toBeNull();
    });
  });

  scenario("Judge Checkpoint stays when a HIL Check is added", ({ given, when, then }) => {
    given("a Turn that already has a JudgeCheckpoint", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
      world.attachments.addJudge(world.turn!, "stories-scenarios");
    });
    when("the operator adds a HILCheck to that Turn", () => {
      world.attachments.addHil(world.turn!, new HILCheck("human ok"));
    });
    then("that Turn has the JudgeCheckpoint", () => {
      expect(world.turn?.judgeCheckpoint?.rubric).toBe("stories-scenarios");
    }).and("that Turn has the HILCheck", () => {
      expect(world.turn?.hilCheck?.validation).toBe("human ok");
    });
  });
});
