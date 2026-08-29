/**
 * Domain wraps for Plan / Workflow / Turn — Clean Engineering companions
 * for Compose Plan acceptance tests (/plan /small-work).
 */

export type TicketStateName = "Backlog" | "In Progress" | "Done";

export class ToolCall {
  constructor(
    public toolset: string,
    public name: string,
  ) {}
}

export class HILCheck {
  constructor(public validation: string | null = null) {}
}

export class JudgeCheckpoint {
  constructor(
    public rubric: string,
    public judgeResult: string | null = null,
  ) {}
}

export class Turn {
  action = "";
  fidelity = "";
  format = "";
  context = "";
  toolKeys: string[] = [];
  toolCalls: ToolCall[] = [];
  state: TicketStateName = "Backlog";
  result: string | null = null;
  hilCheck: HILCheck | null = null;
  judgeCheckpoint: JudgeCheckpoint | null = null;
}

export class Workflow {
  constructor(public name: string) {}
}

export class Workspace {
  plans: Plan[] = [];

  associate(plan: Plan): void {
    if (!this.plans.includes(plan)) {
      this.plans.push(plan);
    }
    plan.workspace = this;
  }
}

export class Plan {
  workspace: Workspace | null = null;
  turns: Turn[] = [];
  workflowName = "";

  constructor(
    public name: string,
    public workflow: Workflow | null = null,
  ) {
    if (workflow) {
      this.workflowName = workflow.name;
    }
  }

  addTurn(fields: Partial<Turn> & { toolCalls?: ToolCall[] } = {}): Turn {
    const turn = new Turn();
    Object.assign(turn, fields);
    if (fields.toolCalls) {
      turn.toolCalls = [...fields.toolCalls];
    }
    turn.state = "Backlog";
    this.turns.push(turn);
    return turn;
  }

  editTurn(turn: Turn, fields: Partial<Turn>): Turn {
    Object.assign(turn, fields);
    return turn;
  }

  deleteTurn(turn: Turn): void {
    this.turns = this.turns.filter((t) => t !== turn);
  }
}

/** Prebaked small-work Workflow Turns (Bdd only — Plan does not inject CE). */
const SMALL_WORK_TURNS: Array<Partial<Turn>> = [
  {
    action: "Generate",
    fidelity: "behavior",
    format: "markdown",
    context: "root-cause",
    toolKeys: ["context_tools.bdd.bdd:Bdd"],
  },
  {
    action: "Generate",
    fidelity: "scenarios",
    format: "markdown",
    context: "fix-one-issue",
    toolKeys: ["context_tools.bdd.bdd:Bdd"],
  },
];

export class PlanCommands {
  smallWork(workspace: Workspace, context: string): Plan {
    const workflow = new Workflow("small-work");
    const plan = new Plan("small-work", workflow);
    workspace.associate(plan);
    for (const template of SMALL_WORK_TURNS) {
      const turn = plan.addTurn(template);
      turn.context = [template.context, context].filter(Boolean).join(" ").trim();
    }
    return plan;
  }

  plan(workspace: Workspace, workflowName: string, context = ""): Plan {
    const workflow = new Workflow(workflowName);
    const plan = new Plan(workflowName, workflow);
    workspace.associate(plan);
    if (context) {
      plan.addTurn({ action: "Generate", context });
    }
    return plan;
  }
}

export class TurnAttachments {
  addHil(turn: Turn, hil: HILCheck = new HILCheck()): HILCheck {
    turn.hilCheck = hil;
    return hil;
  }

  editHil(turn: Turn, hil: HILCheck): HILCheck {
    turn.hilCheck = hil;
    return hil;
  }

  deleteHil(turn: Turn): void {
    turn.hilCheck = null;
  }

  addJudge(turn: Turn, rubric: string): JudgeCheckpoint {
    const check = new JudgeCheckpoint(rubric);
    turn.judgeCheckpoint = check;
    return check;
  }

  editJudge(turn: Turn, rubric: string): JudgeCheckpoint {
    if (!turn.judgeCheckpoint) {
      turn.judgeCheckpoint = new JudgeCheckpoint(rubric);
    } else {
      turn.judgeCheckpoint.rubric = rubric;
    }
    return turn.judgeCheckpoint;
  }

  deleteJudge(turn: Turn): void {
    turn.judgeCheckpoint = null;
  }
}
