const fs = require("fs");
const path = require("path");

const NOTICE = ".cursor/prompt-notify-toast.json";
// How often the notice files are read again: often enough that a toast shows while the call it names is still running.
const POLL_INTERVAL_MS = 300;

/**
 * The message a notice file holds; empty while the file holds no notice. The notifier writes the file whole, but a
 * read can land on it half written, which is no notice yet: the next poll reads it again. A file that is written
 * whole (it ends its JSON object) and still does not parse is broken: that raises, so the watcher reports it.
 */
function messageFromNotice(raw) {
  if (!raw.trimEnd().endsWith("}")) {
    return "";
  }
  const body = JSON.parse(raw);
  return typeof body.message === "string" ? body.message.trim() : "";
}

function noticePath(folder) {
  return path.join(folder, NOTICE);
}

/**
 * Polls the notice file of each workspace folder and hands each new message to onMessage. fs.watchFile is
 * process-global per path: the first caller keeps its interval, and VS Code's suspended watcher uses 5007ms, so a
 * later watchFile misses a rewrite until that poll. Reading the file on our own timer does not join that StatWatcher.
 */
class NoticeWatcher {
  constructor(watching) {
    this.folders = watching.folders;
    this.onMessage = watching.onMessage;
    this.onBroken = watching.onBroken || ((file, err) => console.error(`prompt-notify: ${file} is not a notice: ${err.message}`));
    this.seen = watching.seen || new Map();
    this.fileSystem = watching.fs || fs;
    this.intervalMs = watching.intervalMs || POLL_INTERVAL_MS;
    this.files = new Set();
    this.pending = false;
  }

  start() {
    this.sync();
    for (const file of this.files) {
      this.remember(file);
    }
    this.timer = setInterval(() => this.poll(), this.intervalMs);
    return { sync: () => this.sync(), dispose: () => clearInterval(this.timer) };
  }

  sync() {
    this.files.clear();
    for (const folder of this.folders() || []) {
      this.files.add(noticePath(folder));
    }
  }

  /** What each file holds when watching starts, so a notice already there is not shown again. */
  remember(file) {
    try {
      this.seen.set(file, this.fileSystem.readFileSync(file, "utf8"));
    } catch {
      this.seen.delete(file);
    }
  }

  poll() {
    this.sync();
    const current = [...this.files];
    if (this.pending || current.length === 0) {
      return;
    }
    this.pending = true;
    let left = current.length;
    for (const file of current) {
      this.fileSystem.readFile(file, "utf8", (err, raw) => {
        left -= 1;
        this.pending = left !== 0;
        this.read(file, err, raw);
      });
    }
  }

  read(file, err, raw) {
    if (!err) {
      this.deliver(file, raw);
      return;
    }
    if (err.code === "ENOENT") {
      this.seen.delete(file);
    }
  }

  deliver(file, raw) {
    if (this.seen.get(file) === raw) {
      return;
    }
    let message;
    try {
      message = messageFromNotice(raw);
    } catch (err) {
      this.seen.set(file, raw);
      this.onBroken(file, err);
      return;
    }
    if (!message) {
      return;
    }
    this.seen.set(file, raw);
    this.onMessage(message, file);
  }
}

function createNoticeWatcher(watching) {
  return new NoticeWatcher(watching).start();
}

module.exports = {
  NOTICE,
  messageFromNotice,
  noticePath,
  createNoticeWatcher,
};
