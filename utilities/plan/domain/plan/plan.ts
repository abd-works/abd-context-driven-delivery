/**
 * Domain wraps for Plan / Workflow / Turn — Clean Engineering companions
 * for Compose Plan acceptance tests (flow + tickets; no planned-turn list).
 */

export type TicketStateName = "Backlog" | "In Progress" | "Done";

export class ToolCall {
  constructor(
    public toolset: string,
    public name: string,
  ) {}
}

export class HILCheck {
  constructor(public prompt: string | null = null, public validation: string | null = null) {}
}

export class JudgeCheckpoint {
  constructor(
    public rubric: string,
    public judgeResult: string | null = null,
  ) {}
}

/** Behavior for one Workflow Status column — lives in workflow/flows/{name}.yaml. */
export class FlowState {
  tools: string[] = [];
  action: string | null = null;
  utilities: string[] = [];
  prose: string | null = null;
  hil = false;
  judgeRubric: string | null = null;

  constructor(public name: string) {}
}

export class FlowFile {
  owner: string | null = null;
  projectNumber: number | null = null;
  states: FlowState[] = [];

  constructor(public name: string) {}

  configureState(name: string, fields: Partial<FlowState> = {}): FlowState {
    let state = this.states.find((s) => s.name === name);
    if (!state) {
      state = new FlowState(name);
      this.states.push(state);
    }
    Object.assign(state, fields);
    return state;
  }
}

export class Turn {
  action = "";
  fidelity = "";
  format = "";
  context = "";
  toolKeys: string[] = [];
  toolCalls: ToolCall[] = [];
  state: TicketStateName = "Backlog";
  ticketNumber: number | null = null;
  flowState: string | null = null;
  result: string | null = null;
  hilCheck: HILCheck | null = null;
  judgeCheckpoint: JudgeCheckpoint | null = null;
}

export class Workflow {
  projectNumber: number | null = null;
  throwaway = false;
  flowFile: FlowFile;

  constructor(public name: string) {
    this.flowFile = new FlowFile(name);
  }

  save(owner: string, projectNumber: number): FlowFile {
    this.throwaway = false;
    this.projectNumber = projectNumber;
    this.flowFile.owner = owner;
    this.flowFile.projectNumber = projectNumber;
    return this.flowFile;
  }

  composeThrowaway(): FlowFile {
    this.throwaway = true;
    this.projectNumber = null;
    return this.flowFile;
  }
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
  /** Tickets on this Plan — not a planned-turn list. */
  tickets: number[] = [];
  /** Turns created when tickets enter flow states (runtime). */
  turns: Turn[] = [];
  workflowName = "";
  finished = false;

  constructor(
    public name: string,
    public workflow: Workflow | null = null,
  ) {
    if (workflow) {
      this.workflowName = workflow.name;
    }
  }

  setTickets(numbers: number[]): void {
    this.tickets = [...numbers];
  }

  /** Entering a flow state creates a real Turn (not a planned-turn add). */
  enterState(ticketNumber: number, stateName: string): Turn {
    const turn = new Turn();
    turn.ticketNumber = ticketNumber;
    turn.flowState = stateName;
    turn.state = "In Progress";
    const behavior = this.workflow?.flowFile.states.find((s) => s.name === stateName);
    if (behavior) {
      turn.action = behavior.action ?? "";
      turn.toolKeys = [...behavior.tools];
      if (behavior.hil) {
        turn.hilCheck = new HILCheck(behavior.prose);
      }
      if (behavior.judgeRubric) {
        turn.judgeCheckpoint = new JudgeCheckpoint(behavior.judgeRubric);
      }
    }
    this.turns.push(turn);
    return turn;
  }

  finishPlan(): void {
    this.finished = true;
    this.tickets = [];
  }
}

/** Prebaked small-work Workflow states (Bdd only — Plan does not inject CE). */
const SMALL_WORK_STATES: Array<Partial<FlowState> & { name: string }> = [
  {
    name: "Root Cause",
    action: "Generate",
    tools: ["context_tools.bdd.bdd:Bdd"],
    prose: "root-cause",
  },
  {
    name: "Fix",
    action: "Generate",
    tools: ["context_tools.bdd.bdd:Bdd"],
    prose: "fix-one-issue",
  },
];

export class PlanCommands {
  smallWork(workspace: Workspace, context: string, tickets: number[] = []): Plan {
    const workflow = new Workflow("small-work");
    for (const template of SMALL_WORK_STATES) {
      const { name, ...fields } = template;
      workflow.flowFile.configureState(name, {
        ...fields,
        prose: [fields.prose, context].filter(Boolean).join(" ").trim(),
      });
    }
    const plan = new Plan("small-work", workflow);
    plan.setTickets(tickets);
    workspace.associate(plan);
    return plan;
  }

  plan(
    workspace: Workspace,
    workflowName: string,
    tickets: number[] = [],
  ): Plan {
    const workflow = new Workflow(workflowName);
    const plan = new Plan(workflowName, workflow);
    plan.setTickets(tickets);
    workspace.associate(plan);
    return plan;
  }

  startTicket(plan: Plan, flow: string, number: number): Turn {
    if (!plan.tickets.includes(number)) {
      plan.tickets.push(number);
    }
    plan.workflowName = flow || plan.workflowName;
    const first =
      plan.workflow?.flowFile.states[0]?.name ?? "In Progress";
    if (!flow) {
      const turn = new Turn();
      turn.ticketNumber = number;
      turn.flowState = null;
      turn.state = "In Progress";
      plan.turns.push(turn);
      return turn;
    }
    return plan.enterState(number, first);
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
