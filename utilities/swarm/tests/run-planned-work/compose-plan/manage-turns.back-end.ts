/**
 * Acceptance: Manage Turns (back-end).
 * Sources: plan-and-swarm-sketch.md; grill-answers.md tick 13; manage-turns.md
 */

import { story, scenario, expect } from "../../story-test";
import { Plan, ToolCall, Turn } from "../../../domain/plan/plan";
import {
  aPlanWithGenerateTurn,
  aWorkspaceWithWorkflow,
  freshWorld,
  ComposeWorld,
} from "./givens";

const world: ComposeWorld = freshWorld();
let hanging: Turn | null = null;

story("Manage Turns", () => {
  scenario("Add a Turn in Backlog", ({ given, when, then }) => {
    given("a Plan compose-judged-plan associated with a Workspace", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
    });
    when("the operator adds a Turn with action generate fidelity story_map", () => {
      aPlanWithGenerateTurn(world);
    });
    then("that Plan shows the Turn in sequence", () => {
      expect(world.plan?.turns.length).toBe(1);
    })
      .and("that Turn TicketState is Backlog", () => {
        expect(world.turn?.state).toBe("Backlog");
      })
      .and("that Turn holds action generate fidelity story_map", () => {
        expect(world.turn?.action).toBe("generate");
        expect(world.turn?.fidelity).toBe("story_map");
      })
      .and("that Turn holds that ToolCall", () => {
        expect(world.turn?.toolCalls[0].toolset).toBe("Stories");
        expect(world.turn?.toolCalls[0].name).toBe("generate");
      });
  });

  scenario("Turn holds multiple tools and one action", ({ given, when, then }) => {
    given("a Plan compose-judged-plan associated with a Workspace", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
    });
    when("the operator adds a Turn with action Sketch and two ToolCalls", () => {
      world.turn = world.plan!.addTurn({
        action: "Sketch",
        toolKeys: ["Stories", "CleanEngineering"],
        toolCalls: [
          new ToolCall("Stories", "Sketch"),
          new ToolCall("CleanEngineering", "Sketch"),
        ],
      });
    });
    then("that Turn action is Sketch", () => {
      expect(world.turn?.action).toBe("Sketch");
    })
      .and("that Turn holds both ToolCalls", () => {
        expect(world.turn?.toolCalls.length).toBe(2);
      })
      .and("that Turn TicketState is Backlog", () => {
        expect(world.turn?.state).toBe("Backlog");
      });
  });

  scenario("CliAgent describes the Turn shape without opening it", ({ given, when, then }) => {
    const described = { action: "", toolKeys: [] as string[], toolCalls: [] as ToolCall[], opened: false, hasPlan: false };
    given("a hanging Turn with action Sketch and tool_keys Stories and CleanEngineering", () => {
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
      .and("CliAgent shows those toolCalls", () => {
        expect(described.toolCalls.length).toBe(2);
      })
      .and("CliAgent does not open that Turn", () => {
        expect(described.opened).toBe(false);
      })
      .and("CliAgent holds no Plan", () => {
        expect(described.hasPlan).toBe(false);
      });
  });

  scenario("CLI opens and finishes the hanging Turn", ({ given, when, then }) => {
    given("that hanging Turn with action Sketch", () => {
      hanging = hanging ?? new Turn();
      hanging.action = "Sketch";
      hanging.state = "Backlog";
    });
    when("the CLI opens that Turn and runs Sketch and finishes that Turn", () => {
      hanging!.state = "In Progress";
      hanging!.result = "sketch complete";
      hanging!.state = "Done";
    });
    then("that Turn holds result", () => {
      expect(hanging?.result).toBe("sketch complete");
    }).and("that Turn still uses TicketState", () => {
      expect(["Backlog", "In Progress", "Done"]).toContain(hanging!.state);
    });
  });

  scenario("Later Turn follows the earlier Turn", ({ given, when, then }) => {
    given("a Plan that already has a Turn Stories generate story_map", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
    });
    when("the operator adds a Turn CleanEngineering generate modules", () => {
      world.plan!.addTurn({
        action: "generate",
        fidelity: "modules",
        toolKeys: ["CleanEngineering"],
        toolCalls: [new ToolCall("CleanEngineering", "generate")],
      });
    });
    then("that Plan shows the Stories Turn before the CleanEngineering Turn", () => {
      expect(world.plan?.turns[0].toolKeys).toContain("Stories");
      expect(world.plan?.turns[1].toolKeys).toContain("CleanEngineering");
    }).and("both Turns TicketState is Backlog", () => {
      expect(world.plan?.turns.every((t) => t.state === "Backlog")).toBe(true);
    });
  });

  scenario("Edit a Turn", ({ given, when, then }) => {
    given("a Plan with a Turn Stories generate story_map", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
    });
    when("the operator edits that Turn fidelity to scenarios", () => {
      world.plan!.editTurn(world.turn!, { fidelity: "scenarios" });
    });
    then("that Turn fidelity is scenarios", () => {
      expect(world.turn?.fidelity).toBe("scenarios");
    })
      .and("that Turn TicketState is still Backlog", () => {
        expect(world.turn?.state).toBe("Backlog");
      })
      .and("that Turn still holds ToolCall Stories generate", () => {
        expect(world.turn?.toolCalls[0].name).toBe("generate");
      });
  });

  scenario("Delete a Turn", ({ given, when, then }) => {
    let ceTurn: Turn;
    given("a Plan with a Stories Turn and a CleanEngineering Turn", () => {
      Object.assign(world, freshWorld());
      aWorkspaceWithWorkflow(world, "compose-judged-plan");
      aPlanWithGenerateTurn(world);
      ceTurn = world.plan!.addTurn({
        action: "generate",
        toolKeys: ["CleanEngineering"],
        toolCalls: [new ToolCall("CleanEngineering", "generate")],
      });
    });
    when("the operator deletes the CleanEngineering Turn", () => {
      world.plan!.deleteTurn(ceTurn);
    });
    then("that Plan holds the Stories Turn", () => {
      expect(world.plan?.turns.length).toBe(1);
      expect(world.plan?.turns[0].toolKeys).toContain("Stories");
    }).and("that Stories Turn TicketState is still Backlog", () => {
      expect(world.plan?.turns[0].state).toBe("Backlog");
    });
  });
});
