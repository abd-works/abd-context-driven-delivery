const fs = require("fs");
const path = require("path");
const vscode = require("vscode");

const NOTICE = ".cursor/prompt-echo-toast.json";

function readNotice(file, onNotice) {
  fs.readFile(file, "utf8", (err, raw) => {
    if (err) {
      return;
    }
    try {
      const body = JSON.parse(raw);
      const message = typeof body.message === "string" ? body.message.trim() : "";
      if (message) {
        onNotice(message, raw);
      }
    } catch {
      return;
    }
  });
}

function watchWorkspace(context, folder, seen) {
  const file = path.join(folder.uri.fsPath, NOTICE);
  const showIfChanged = () => {
    readNotice(file, (message, raw) => {
      if (seen.get(file) === raw) {
        return;
      }
      seen.set(file, raw);
      vscode.window.showInformationMessage(message);
    });
  };
  fs.watchFile(file, { interval: 300 }, showIfChanged);
  context.subscriptions.push({ dispose: () => fs.unwatchFile(file) });
}

function activate(context) {
  const seen = new Map();
  for (const folder of vscode.workspace.workspaceFolders || []) {
    watchWorkspace(context, folder, seen);
  }
}

function deactivate() {}

module.exports = { activate, deactivate };
