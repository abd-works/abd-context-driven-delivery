/**
 * Shared givens for Compose Plan acceptance tests (flow + tickets).
 */

import {
  Plan,
  PlanCommands,
  Turn,
  TurnAttachments,
  Workspace,
  Workflow,
  ToolCall,
} from "../../domain/plan/plan";

export type ComposeWorld = {
  workspace: Workspace;
  commands: PlanCommands;
  attachments: TurnAttachments;
  plan: Plan | null;
  turn: Turn | null;
  secondPlan: Plan | null;
};

export function freshWorld(): ComposeWorld {
  return {
    workspace: new Workspace(),
    commands: new PlanCommands(),
    attachments: new TurnAttachments(),
    plan: null,
    turn: null,
    secondPlan: null,
  };
}

export function aWorkspaceWithWorkflow(
  world: ComposeWorld,
  workflowName: string,
): void {
  world.plan = new Plan(workflowName, new Workflow(workflowName));
  world.workspace.associate(world.plan);
}

export function aPlanWithTicketOnFix(world: ComposeWorld): void {
  if (!world.plan) {
    world.plan = world.commands.plan(world.workspace, "compose-judged-plan", [14]);
  }
  world.plan.workflow!.flowFile.configureState("Fix", {
    action: "generate",
    tools: ["Stories"],
  });
  world.turn = world.plan.enterState(14, "Fix");
  world.turn.toolCalls = [new ToolCall("Stories", "generate")];
}
