const vscode = require("vscode");

const NOTICE = ".cursor/prompt-echo-toast.json";

async function showNotice(uri) {
  try {
    const raw = await vscode.workspace.fs.readFile(uri);
    const body = JSON.parse(Buffer.from(raw).toString("utf8"));
    const message = typeof body.message === "string" ? body.message.trim() : "";
    if (message) {
      vscode.window.showInformationMessage(message);
    }
  } catch {
    return;
  }
}

function activate(context) {
  const watcher = vscode.workspace.createFileSystemWatcher(`**/${NOTICE}`);
  watcher.onDidCreate(showNotice);
  watcher.onDidChange(showNotice);
  context.subscriptions.push(watcher);
  for (const folder of vscode.workspace.workspaceFolders || []) {
    showNotice(vscode.Uri.joinPath(folder.uri, NOTICE));
  }
}

function deactivate() {}

module.exports = { activate, deactivate };
