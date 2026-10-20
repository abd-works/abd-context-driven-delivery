const fs = require("fs");
const path = require("path");

const NOTICE = ".cursor/prompt-notify-toast.json";

function messageFromNotice(raw) {
  let body;
  try {
    body = JSON.parse(raw);
  } catch {
    return "";
  }
  return typeof body.message === "string" ? body.message.trim() : "";
}

function noticePath(folder) {
  return path.join(folder, NOTICE);
}

function remember(io, file, seen) {
  try {
    seen.set(file, io.readFileSync(file, "utf8"));
  } catch {
    seen.delete(file);
  }
}

/**
 * Poll notice file contents. fs.watchFile is process-global per path: the
 * first caller keeps its interval, and VS Code's suspended watcher uses
 * 5007ms, so a later watchFile misses a rewrite until that poll. Reading
 * the file on our own timer does not join that StatWatcher.
 */
function createNoticeWatcher(options) {
  const seen = options.seen || new Map();
  const io = options.fs || fs;
  const intervalMs = options.intervalMs || 300;
  const files = new Set();
  let pending = false;

  function sync() {
    files.clear();
    for (const folder of options.folders() || []) {
      files.add(noticePath(folder));
    }
  }

  function deliver(file, raw) {
    if (seen.get(file) === raw) {
      return;
    }
    const message = messageFromNotice(raw);
    if (!message) {
      return;
    }
    seen.set(file, raw);
    options.onMessage(message, file);
  }

  sync();
  for (const file of files) {
    remember(io, file, seen);
  }

  const timer = setInterval(() => {
    sync();
    if (pending) {
      return;
    }
    const current = [...files];
    if (current.length === 0) {
      return;
    }
    pending = true;
    let left = current.length;
    for (const file of current) {
      io.readFile(file, "utf8", (err, raw) => {
        left -= 1;
        if (left === 0) {
          pending = false;
        }
        if (err) {
          if (err.code === "ENOENT") {
            seen.delete(file);
          }
          return;
        }
        deliver(file, raw);
      });
    }
  }, intervalMs);

  return {
    sync,
    dispose() {
      clearInterval(timer);
    },
  };
}

module.exports = {
  NOTICE,
  messageFromNotice,
  noticePath,
  createNoticeWatcher,
};
