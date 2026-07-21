/**
 * Serve the repo root so Story Demo examples can resolve /contexts/... imports.
 *
 *   node contexts/ux/story-demo/run.mjs
 *   PORT=3001 node contexts/ux/story-demo/run.mjs
 */

import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../..");
const port = process.env.PORT || "3000";
const examplePath =
  process.env.STORY_DEMO_EXAMPLE ||
  "/contexts/ux/examples/manage-customer-orders/place-new-order/place-new-order.html";

const url = `http://localhost:${port}${examplePath}`;

console.log(`Story Demo — serving repo root`);
console.log(`  root: ${repoRoot}`);
console.log(`  open: ${url}`);
console.log(``);

const child = spawn(
  "npx",
  ["--yes", "serve", "-l", port, repoRoot],
  { stdio: "inherit", shell: true, cwd: repoRoot },
);

child.on("exit", (code) => process.exit(code ?? 0));
