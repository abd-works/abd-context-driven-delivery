// engine/engine.ts
import type { ICounter } from "../counter/counter.js";
import { Counter } from "../counter/counter.js";
import type { IContextFolder } from "../context_folder/context_folder.js";
import { ContextFolder } from "../context_folder/context_folder.js";
import type { IBot } from "../bot/bot.js";
import { Bot } from "../bot/bot.js";
import type { IBehavior } from "../behavior/behavior.js";
import { Behavior } from "../behavior/behavior.js";
import type { IInstructions } from "../instructions/instructions.js";
import { Instructions } from "../instructions/instructions.js";

export class Engine {
  counter: ICounter;
  contextFolder: IContextFolder;
  bot: IBot;
  behavior: IBehavior;
  instructions: IInstructions;

  constructor(counter?: ICounter, contextFolder?: IContextFolder, bot?: IBot, behavior?: IBehavior, instructions?: IInstructions) {
    this.counter = counter ?? new Counter();
    this.contextFolder = contextFolder ?? new ContextFolder();
    this.bot = bot ?? new Bot();
    this.behavior = behavior ?? new Behavior();
    this.instructions = instructions ?? new Instructions();
  }
}
