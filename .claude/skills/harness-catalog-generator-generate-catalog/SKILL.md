---
name: harness-catalog-generator-generate-catalog
description: >-
  Render the whole catalog into ``out_root`` with Foundry chrome.
  No output is ever written outside ``out_root``.
  ``brand`` is a collection name under the brands folder, or a path to a
  brand folder; empty uses bundled abd-works.
---

Render the whole catalog into ``out_root`` with Foundry chrome.
No output is ever written outside ``out_root``.
``brand`` is a collection name under the brands folder, or a path to a
brand folder; empty uses bundled abd-works.

Use MCP tool: `catalog.generate_catalog(brand: 'str | Path' = '')`
