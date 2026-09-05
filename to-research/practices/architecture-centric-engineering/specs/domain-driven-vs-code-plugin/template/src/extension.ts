// extension.ts — VS Code extension entry point
import * as vscode from "vscode";
import { EngineView } from "./engine/view/engine_view";

export function activate(context: vscode.ExtensionContext): void {
  const disposable = vscode.commands.registerCommand(
    "extension.viewEngine",  // replace with your extension.commandId from package.json
    () => {
      EngineView.createOrShow(context.extensionUri);
    }
  );

  context.subscriptions.push(disposable);
}

export function deactivate(): void {
  // Cleanup if needed
}
