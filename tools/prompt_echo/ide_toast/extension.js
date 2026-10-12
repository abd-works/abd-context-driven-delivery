const fs = require("fs");
const path = require("path");
const vscode = require("vscode");
const { createNoticeWatcher } = require("./watch_notice");

function activate(context) {
  const watcher = createNoticeWatcher({
    folders() {
      return (vscode.workspace.workspaceFolders || []).map((folder) => folder.uri.fsPath);
    },
    onMessage(message) {
      vscode.window.showInformationMessage(message);
    },
  });
  context.subscriptions.push({ dispose: () => watcher.dispose() });
  context.subscriptions.push(
    vscode.workspace.onDidChangeWorkspaceFolders(() => watcher.sync()),
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
