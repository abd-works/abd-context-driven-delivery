/**
 * Load [data-include] HTML fragments (story-folder screens) into the composed page.
 * Run before mount-generated-mockup.js hydrates controls.
 */

async function includeFragments(root = document) {
  const nodes = [...root.querySelectorAll("[data-include]")];
  for (const el of nodes) {
    const src = el.getAttribute("data-include");
    if (!src) continue;
    const url = new URL(src, document.baseURI).href;
    const res = await fetch(url);
    if (!res.ok) {
      console.warn(`[compose] failed to load ${src}:`, res.status);
      continue;
    }
    const html = await res.text();
    el.outerHTML = html;
  }
  // Nested includes (e.g. cart regions) — one more pass if any remain.
  if (root.querySelector("[data-include]")) {
    await includeFragments(root);
  }
}

await includeFragments(document);
