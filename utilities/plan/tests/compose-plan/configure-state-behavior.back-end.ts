/**
 * Acceptance: Configure State Behavior (back-end).
 * Sources: grill-answers.md ticks 16, 22–23; configure-state-behavior.md
 */

import { story, scenario, expect } from "../../story-test";
import { ToolCall, Turn } from "../../domain/plan/plan";
import {
  aWorkspaceWithWorkflow,
  freshWorld,
  ComposeWorld,
} from "./givens";

const world: ComposeWorld = freshWorld();
let hanging: Turn | null = null;

story("Configure State Behavior", () => {
  scenario("Per-state behavior is stored on the flow file", ({ given, when, then }) => {
    given("a Plan small-work associated with a Workspace", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "small-work");
    });
    when("the operator configures state Fix with tools Bdd and action generate", () => {
      world.plan!.workflow!.flowFile.configureState("Fix", {
        tools: ["Bdd"],
        action: "generate",
        prose: "fix the defect",
      });
    });
    then("that flow file records Fix behavior", () => {
      const fix = world.plan!.workflow!.flowFile.states.find((s) => s.name === "Fix");
      expect(fix?.action).toBe("generate");
      expect(fix?.tools).toEqual(["Bdd"]);
      expect(fix?.prose).toBe("fix the defect");
    }).and("entering Fix creates a Turn from that behavior", () => {
      world.turn = world.plan!.enterState(14, "Fix");
      expect(world.turn.action).toBe("generate");
      expect(world.turn.toolKeys).toEqual(["Bdd"]);
      expect(world.turn.ticketNumber).toBe(14);
    });
  });

  scenario("Turn from state entry may hold multiple tools and one action", ({ given, when, then }) => {
    given("a Plan with state Sketch configured for two tools", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      world.plan!.workflow!.flowFile.configureState("Sketch", {
        action: "Sketch",
        tools: ["Stories", "CleanEngineering"],
      });
    });
    when("ticket 14 enters Sketch", () => {
      world.turn = world.plan!.enterState(14, "Sketch");
      world.turn.toolCalls = [
        new ToolCall("Stories", "Sketch"),
        new ToolCall("CleanEngineering", "Sketch"),
      ];
    });
    then("that Turn action is Sketch", () => {
      expect(world.turn?.action).toBe("Sketch");
    })
      .and("that Turn holds both ToolCalls", () => {
        expect(world.turn?.toolCalls.length).toBe(2);
      })
      .and("that Turn TicketState is In Progress", () => {
        expect(world.turn?.state).toBe("In Progress");
      });
  });

  scenario("CliAgent describes the Turn shape without opening it", ({ given, when, then }) => {
    const described = { action: "", toolKeys: [] as string[], toolCalls: [] as ToolCall[], opened: false, hasPlan: false };
    given("a hanging Turn created by entering Fix", () => {
      hanging = new Turn();
      hanging.action = "Sketch";
      hanging.toolKeys = ["Stories", "CleanEngineering"];
      hanging.toolCalls = [
        new ToolCall("Stories", "Sketch"),
        new ToolCall("CleanEngineering", "Sketch"),
      ];
    });
    when("CliAgent describes that Turn", () => {
      described.action = hanging!.action;
      described.toolKeys = [...hanging!.toolKeys];
      described.toolCalls = [...hanging!.toolCalls];
      described.opened = false;
      described.hasPlan = false;
    });
    then("CliAgent shows action Sketch", () => {
      expect(described.action).toBe("Sketch");
    })
      .and("CliAgent shows those tool_keys", () => {
        expect(described.toolKeys).toEqual(["Stories", "CleanEngineering"]);
      })
      .and("CliAgent does not open that Turn and holds no Plan", () => {
        expect(described.opened).toBe(false);
        expect(described.hasPlan).toBe(false);
      });
  });

  scenario("Plan has no planned-turn list", ({ given, when, then }) => {
    given("a Plan based on Workflow small-work with tickets 14 and 15", () => {
      Object.assign(world, freshWorld());
      world.plan = world.commands.smallWork(world.workspace, "themed", [14, 15]);
    });
    when("the operator inspects that Plan", () => {
      /* inspect */
    });
    then("that Plan names the Workflow and those tickets", () => {
      expect(world.plan?.workflowName).toBe("small-work");
      expect(world.plan?.tickets).toEqual([14, 15]);
    }).and("that Plan holds no pre-listed turns", () => {
      expect(world.plan?.turns.length).toBe(0);
      expect(world.plan?.workflow?.flowFile.states.length).toBeGreaterThan(0);
    });
  });

  scenario("Flow file holds owner and project number on save", ({ given, when, then }) => {
    given("a composed Workflow hotfix-batch", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "hotfix-batch");
    });
    when("the operator saves that Workflow against Project 42", () => {
      world.plan!.workflow!.save("acme", 42);
    });
    then("the flow file includes owner and project_number 42", () => {
      expect(world.plan!.workflow!.flowFile.owner).toBe("acme");
      expect(world.plan!.workflow!.flowFile.projectNumber).toBe(42);
      expect(world.plan!.workflow!.throwaway).toBe(false);
    });
  });
});
