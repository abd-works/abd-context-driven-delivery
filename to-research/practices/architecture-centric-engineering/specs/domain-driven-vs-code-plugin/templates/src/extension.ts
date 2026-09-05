// extension.ts — VS Code extension entry point (composition root)
import * as vscode from 'vscode';
import { EngineView } from './engine/view/engine_view.js';

export function activate(context: vscode.ExtensionContext): void {
  const disposable = vscode.commands.registerCommand(
    '{{extension.commandId}}',   // matches package.json contributes.commands[].command
    () => {
      EngineView.createOrShow(context.extensionUri);
    }
  );

  context.subscriptions.push(disposable);
}

export function deactivate(): void {}
