const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { createNoticeWatcher } = require("./watch_notice");

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function writeNotice(file, message) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const body = JSON.stringify({
    message,
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
  });
  fs.writeFileSync(file, body + "\n");
}

async function rewriteWhileSlowWatcherOwnsThePath() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "toast-spec-"));
  const file = path.join(root, ".cursor", "prompt-notify-toast.json");
  writeNotice(file, "already on disk");
  const slow = () => {};
  fs.watchFile(file, { persistent: false, interval: 5007 }, slow);
  const shown = [];
  const watcher = createNoticeWatcher({
    folders: () => [root],
    onMessage: (message) => shown.push(message),
    intervalMs: 50,
  });
  await wait(200);
  assert.deepStrictEqual(shown, [], "existing notice is not a new toast");
  writeNotice(file, "chat mm3e story map no yaml edited file → rules : Stories, story_map");
  await wait(800);
  watcher.dispose();
  fs.unwatchFile(file, slow);
  fs.rmSync(root, { recursive: true, force: true });
  assert.deepStrictEqual(shown, [
    "chat mm3e story map no yaml edited file → rules : Stories, story_map",
  ]);
}

async function secondRewriteShowsAndDuplicateDoesNot() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "toast-spec-"));
  const file = path.join(root, ".cursor", "prompt-notify-toast.json");
  writeNotice(file, "baseline");
  const shown = [];
  const watcher = createNoticeWatcher({
    folders: () => [root],
    onMessage: (message) => shown.push(message),
    intervalMs: 50,
  });
  await wait(120);
  const first = JSON.stringify({ message: "one", at: "2026-10-11T18:41:14Z" }) + "\n";
  fs.writeFileSync(file, first);
  await wait(200);
  fs.writeFileSync(file, first);
  await wait(200);
  fs.writeFileSync(file, JSON.stringify({ message: "two", at: "2026-10-11T18:42:35Z" }) + "\n");
  await wait(200);
  watcher.dispose();
  fs.rmSync(root, { recursive: true, force: true });
  assert.deepStrictEqual(shown, ["one", "two"]);
}

async function everyWorkspaceFolderReachesShow() {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "toast-spec-"));
  const roots = [path.join(parent, "a"), path.join(parent, "b")];
  const shown = [];
  const watcher = createNoticeWatcher({
    folders: () => roots,
    onMessage: (message, file) => shown.push({ message, file }),
    intervalMs: 50,
  });
  await wait(80);
  writeNotice(path.join(roots[0], ".cursor", "prompt-notify-toast.json"), "from-a");
  writeNotice(path.join(roots[1], ".cursor", "prompt-notify-toast.json"), "from-b");
  await wait(250);
  watcher.dispose();
  fs.rmSync(parent, { recursive: true, force: true });
  assert.deepStrictEqual(
    shown.map((item) => item.message).sort(),
    ["from-a", "from-b"],
  );
}

async function extensionActivateReachesShowInformationMessage() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "toast-spec-"));
  const file = path.join(root, ".cursor", "prompt-notify-toast.json");
  writeNotice(file, "already showing");
  const shown = [];
  const Module = require("module");
  const original = Module._load;
  Module._load = function (request, parent, isMain) {
    if (request === "vscode") {
      return {
        window: {
          showInformationMessage(message) {
            shown.push(message);
          },
        },
        workspace: {
          workspaceFolders: [{ uri: { fsPath: root } }],
          onDidChangeWorkspaceFolders() {
            return { dispose() {} };
          },
        },
      };
    }
    return original.apply(this, arguments);
  };
  const extensionPath = require.resolve("./extension");
  delete require.cache[extensionPath];
  const { activate } = require("./extension");
  const subscriptions = [];
  activate({ subscriptions });
  await wait(80);
  assert.deepStrictEqual(shown, []);
  writeNotice(file, "chat mm3e story map no yaml edited file → rules : Stories, story_map");
  await wait(500);
  for (const item of subscriptions) {
    item.dispose();
  }
  Module._load = original;
  fs.rmSync(root, { recursive: true, force: true });
  assert.deepStrictEqual(shown, [
    "chat mm3e story map no yaml edited file → rules : Stories, story_map",
  ]);
}

(async () => {
  await rewriteWhileSlowWatcherOwnsThePath();
  await secondRewriteShowsAndDuplicateDoesNot();
  await everyWorkspaceFolderReachesShow();
  await extensionActivateReachesShowInformationMessage();
  console.log("watch_notice_spec passed");
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
