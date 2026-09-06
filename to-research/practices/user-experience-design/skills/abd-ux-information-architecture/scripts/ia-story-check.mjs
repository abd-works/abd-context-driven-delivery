#!/usr/bin/env node
/**
 * ia-story-check.mjs
 * Cross-checks a story-map.md against an initial-ia.md story trace table.
 * Reports every GM story that is absent from the IA story trace.
 *
 * Usage:
 *   node ia-story-check.mjs --map <story-map.md> --ia <initial-ia.md>
 *
 * Exit codes:
 *   0 = all GM stories covered
 *   1 = gaps found (list printed to stdout)
 */

import { readFileSync } from 'fs';

function parseArgs() {
  const args = process.argv.slice(2);
  const get = flag => {
    const i = args.indexOf(flag);
    return i !== -1 ? args[i + 1] : null;
  };
  const map = get('--map');
  const ia  = get('--ia');
  if (!map || !ia) {
    console.error('Usage: ia-story-check.mjs --map <story-map.md> --ia <initial-ia.md>');
    process.exit(2);
  }
  return { map, ia };
}

function extractGmStories(storyMapText) {
  const stories = [];
  for (const line of storyMapText.split('\n')) {
    const m = line.match(/\(S\)\s+GM\s+-->\s+(.+)/);
    if (m) stories.push(m[1].trim());
  }
  return stories;
}

function extractTraceStories(iaText) {
  // Grab the story trace table rows — first column between pipes
  const tableStart = iaText.indexOf('## Story trace table');
  if (tableStart === -1) return [];
  const section = iaText.slice(tableStart);
  const covered = new Set();
  for (const line of section.split('\n')) {
    if (!line.startsWith('|')) continue;
    const cols = line.split('|').map(c => c.trim()).filter(Boolean);
    if (cols.length < 2) continue;
    const story = cols[0];
    if (story === 'Story' || story.startsWith('---')) continue;
    covered.add(story.toLowerCase());
  }
  return covered;
}

/** Normalise a story title for fuzzy matching:
 *  strip punctuation, lowercase, collapse whitespace */
function norm(s) {
  return s.toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
}

function main() {
  const { map, ia } = parseArgs();
  const mapText = readFileSync(map, 'utf8');
  const iaText  = readFileSync(ia,  'utf8');

  const gmStories  = extractGmStories(mapText);
  const traceSet   = extractTraceStories(iaText);

  // Build a normalised lookup from the trace
  const normTrace = new Set([...traceSet].map(norm));

  const missing = [];
  for (const story of gmStories) {
    const n = norm(story);
    const storyWords = n.split(' ').filter(w => w.length > 3);
    const covered =
      normTrace.has(n) ||
      [...normTrace].some(t => {
        const traceWords = t.split(' ').filter(w => w.length > 3);
        // Either all story keywords appear in trace, or all trace keywords appear in story
        return (
          storyWords.every(w => t.includes(w)) ||
          traceWords.every(w => n.includes(w))
        );
      });
    if (!covered) missing.push(story);
  }

  const total   = gmStories.length;
  const covered = total - missing.length;

  console.log(`\n[ia-story-check] ${covered}/${total} GM stories covered in story trace\n`);

  if (missing.length === 0) {
    console.log('✅  All GM stories are represented in the IA story trace.');
    process.exit(0);
  }

  console.log(`❌  ${missing.length} GM stories not found in story trace:\n`);
  for (const s of missing) console.log(`  - ${s}`);
  console.log('');
  process.exit(1);
}

main();
