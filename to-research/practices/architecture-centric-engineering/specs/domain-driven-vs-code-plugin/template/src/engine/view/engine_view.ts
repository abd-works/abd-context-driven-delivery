// engine/view/engine_view.ts — Server view: owns Engine, delegates to sub-views, handles postMessage
import * as vscode from "vscode";
import * as path from "path";
import * as crypto from "crypto";
import { BaseView } from "../base_view";
import { Engine } from "../engine";
import { CounterServer } from "../../counter/counter_server";
import { CounterView } from "../../counter/view/counter_view";
import { ContextFolderServer } from "../../context_folder/context_folder_server";
import { ContextFolderView } from "../../context_folder/view/context_folder_view";
import { BotServer } from "../../bot/bot_server";
import { BotView } from "../../bot/view/bot_view";
import { BehaviorServer } from "../../behavior/behavior_server";
import { BehaviorView } from "../../behavior/view/behavior_view";
import { InstructionsServer } from "../../instructions/instructions_server";
import { InstructionsView } from "../../instructions/view/instructions_view";
import type { ExecutionSetting } from "../../behavior/behavior";
import type { IBot } from "../../bot/bot";
import type { IBehavior } from "../../behavior/behavior";
import type { IInstructions } from "../../instructions/instructions";

function getNonce(): string {
  return crypto.randomBytes(16).toString("hex");
}

export class EngineView extends BaseView {
  public static currentPanel: EngineView | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private _engine: Engine;
  public counter: CounterView;
  public contextFolder: ContextFolderView;
  public bot: BotView;
  public behavior: BehaviorView;
  public instructions: InstructionsView;
  private _disposables: vscode.Disposable[] = [];

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    super(extensionUri);
    this._panel = panel;

    const counterPath = path.join(extensionUri.fsPath, "persistence", "counter.json");
    const contextFolderPath = path.join(extensionUri.fsPath, "persistence", "context_folder.json");
    const botPath = path.join(extensionUri.fsPath, "persistence", "bot.json");
    const behaviorPath = path.join(extensionUri.fsPath, "persistence", "behavior.json");
    const botConfigDir = path.join(extensionUri.fsPath, "bots");
    const botServer = new BotServer(botPath, botConfigDir);
    const behaviorServer = new BehaviorServer(behaviorPath);
    const instructionsServer = new InstructionsServer();
    this._engine = new Engine(
      new CounterServer(counterPath),
      new ContextFolderServer(contextFolderPath),
      botServer,
      behaviorServer,
      instructionsServer
    ); // server domain (persistence)

    this.counter = new CounterView(
      this._panel,
      this._engine.counter,
      extensionUri
    ); // server view
    this.contextFolder = new ContextFolderView(
      this._panel,
      this._engine.contextFolder,
      extensionUri
    ); // server view
    this.bot = new BotView(
      this._panel,
      this._engine.bot,
      extensionUri
    ); // server view
    this.behavior = new BehaviorView(
      this._panel,
      this._engine.behavior,
      extensionUri
    ); // server view
    this.instructions = new InstructionsView(
      this._panel,
      this._engine.instructions,
      extensionUri
    ); // server view

    // Coordinate: if BotServer already selected a bot (via persistence), forward behaviors
    // Must run after all views (especially instructions) are initialized
    this._syncBehaviorsFromBot(botServer, behaviorServer);

    // Sync instructions from initial behavior state
    this._syncInstructionsFromBehavior();

    this._panel.webview.html = this._getHtml();

    this._panel.webview.onDidReceiveMessage(
      (message: { command: string; [key: string]: unknown }) => {
        this._handleMessage(message);
      },
      null,
      this._disposables
    );

    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
  }

  private _handleMessage(message: { command: string; [key: string]: unknown }): void {
    const { command, ...args } = message;
    const [obj, key] = this._lookup(command);
    const target = (obj as Record<string, unknown>)[key];

    if (typeof target === "function") {
      (target as (...args: unknown[]) => unknown).apply(
        obj,
        Object.values(args)
      );
    } else if ("value" in args) {
      // Setter
      (obj as Record<string, unknown>)[key] = args.value;
    } else {
      // Getter — post the value back
      const value = (obj as Record<string, unknown>)[key];
      if (key === "total") {
        this._panel.webview.postMessage({ total: value });
      } else if (key === "bar") {
        this._panel.webview.postMessage({ fooBar: value });
      } else if (key === "folderPath") {
        this._panel.webview.postMessage({ folderPath: value });
      } else if (key === "name" && command.startsWith("contextFolder.")) {
        this._panel.webview.postMessage({ botName: value });
      }
    }

    // Behavior: setExecutionSetting sends key/value as separate properties
    if (command === "behavior.setExecutionSetting" && "key" in message) {
      this.behavior.setExecutionSetting(message.key as string, message.value as ExecutionSetting);
    }

    // Coordinate: when bot switches, sync to BehaviorServer for persistence
    if (command === "bot.switchBot") {
      this._syncBehaviorsFromBot(this._engine.bot, this._engine.behavior);
    }

    // Coordinate: after behavior navigation commands, sync instructions
    if (command.startsWith("behavior.") && (
      command === "behavior.navigateToBehavior" ||
      command === "behavior.navigateToAction" ||
      command === "behavior.next" ||
      command === "behavior.back" ||
      command === "behavior.closeCurrent" ||
      command === "behavior.requestInit"
    )) {
      this._syncInstructionsFromBehavior();
    }
  }

  /** Forward the selected bot's behavior configs to BehaviorServer. */
  private _syncBehaviorsFromBot(bot: IBot, behavior: IBehavior): void {
    const config = bot.currentBotConfig;
    if (config) {
      behavior.loadBehaviors(config.behaviorNames, config.behaviorConfigs);
      behavior.loadActions(config.baseActionConfigs);
      this._syncInstructionsFromBehavior();
    }
  }

  /** Sync instructions from current behavior/action state. */
  private _syncInstructionsFromBehavior(): void {
    this.instructions.setBehaviorInstructions(
      this._engine.behavior.currentBehavior?.instructions ?? []
    );
    this.instructions.setActionInstructions(
      this._engine.behavior.currentAction?.instructions ?? []
    );
  }

  _lookup(pathStr: string): [object, string] {
    const parts = pathStr.split(".");
    let target: object = this;
    for (let i = 0; i < parts.length - 1; i++) {
      target = (target as Record<string, unknown>)[parts[i]] as object;
    }
    return [target, parts[parts.length - 1]];
  }

  private _getHtml(): string {
    const webview = this._panel.webview;
    const asUri = (p: string[]) =>
      webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "dist", ...p)); // TODO: will hardcoding dist work when the extension is bundled for publishing?
    const nonce = getNonce();
    const counterHtml = this.counter.getHtml(); // delegate; EngineView does not know counter markup
    const contextFolderHtml = this.contextFolder.getHtml();
    const botHtml = this.bot.getHtml();
    const behaviorHtml = this.behavior.getHtml();
    const instructionsHtml = this.instructions.getHtml();

    return this.renderTemplate("dist/engine/view/Engine.html", {
      nonce,
      content: contextFolderHtml + botHtml + counterHtml + behaviorHtml + instructionsHtml,
      themeCssUri: asUri(["view", "theme.css"]).toString(),
      engineCssUri: asUri(["engine", "view", "layout.css"]).toString(),      
      counterClientUri: asUri(["counter", "view", "counter_client.js"]).toString(),
      contextFolderClientUri: asUri(["context_folder", "view", "context_folder_client.js"]).toString(),
      botClientUri: asUri(["bot", "view", "bot_client.js"]).toString(),
      behaviorClientUri: asUri(["behavior", "view", "behavior_client.js"]).toString(),
      instructionsClientUri: asUri(["instructions", "view", "instructions_client.js"]).toString(),
      engineClientUri: asUri(["engine", "view", "engine_client.js"]).toString(),
    });
  }

  public static createOrShow(extensionUri: vscode.Uri): void {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    // If we already have a panel, show it
    if (EngineView.currentPanel) {
      EngineView.currentPanel._panel.reveal(column);
      return;
    }

    // Otherwise, create a new panel
    const panel = vscode.window.createWebviewPanel(
      "agilebot.engineView",
      "Engine View",
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: [vscode.Uri.joinPath(extensionUri, "dist")],
      }
    );

    EngineView.currentPanel = new EngineView(panel, extensionUri);
  }

  public dispose(): void {
    EngineView.currentPanel = undefined;

    this._panel.dispose();

    while (this._disposables.length) {
      const d = this._disposables.pop();
      if (d) {
        d.dispose();
      }
    }
  }
}
