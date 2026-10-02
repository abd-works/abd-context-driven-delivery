#!/usr/bin/env node
/**
 * Rebuild pml-domainmodel app-sandbox map mockup from map_mockup_shell.html
 * and shared story-demo JS. Preserves the hand-laid map body from the current mockup.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const uxRoot = path.resolve(here, "..");
const sandboxMockup = path.resolve(
  uxRoot,
  "../../../paradise-mobile/pml-domainmodel/app-sandbox/my/.context/mockup.html",
);

function stripModuleSyntax(source) {
  return source
    .replace(/^export function /gm, "function ")
    .replace(/^export /gm, "");
}

function read(rel) {
  return fs.readFileSync(path.join(uxRoot, rel), "utf8");
}

function extractMainBody(html) {
  const match = html.match(/<main id="mockup">\s*([\s\S]*?)\s*<\/main>/);
  if (!match) throw new Error("Could not find #mockup body in sandbox mockup.html");
  return match[1]
    .trim()
    .replace(/\s*<p class="key">[\s\S]*?<\/p>\s*/g, "\n");
}

function extractJsonScript(html, id) {
  const match = html.match(new RegExp(`<script id="${id}"[^>]*>([\\s\\S]*?)</script>`));
  if (!match) throw new Error(`Missing #${id} in sandbox mockup.html`);
  return match[1].trim();
}

function extractModelJson(html) {
  const match = html.match(/<!-- ux-map-json:\s*([\s\S]*?)\s*-->/);
  return match ? match[1].trim() : "{}";
}

const current = fs.readFileSync(sandboxMockup, "utf8");
const mapBody = extractMainBody(current);
const storyOutline = extractJsonScript(current, "story-outline");
const screenStories = extractJsonScript(current, "screen-stories");
const modelJson = extractModelJson(current);

const inlineScript = [
  stripModuleSyntax(read("story-demo/screen-tree.js")),
  read("story-demo/bind-flow-zoom.js"),
  read("story-demo/map-mockup-boot.js"),
].join("\n\n");

let output = read("templates/html/map_mockup_shell.html");
output = output
  .replaceAll("@@TITLE@@", "My Paradise")
  .replace("@@MAP_BODY@@", mapBody)
  .replace("@@STORY_OUTLINE@@", storyOutline)
  .replace("@@SCREEN_STORIES@@", screenStories)
  .replace("@@INLINE_SCRIPT@@", inlineScript)
  .replace("@@START_SCREEN@@", "Create Account")
  .replace("@@MODEL_JSON@@", modelJson);

fs.writeFileSync(sandboxMockup, output);
console.log(`rebuilt ${sandboxMockup}`);
