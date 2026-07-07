---
description: A folder's top-level instructions live in a markdown file named after the folder.
globs: **/*.md
---

The top-level instructions for a folder must live in a markdown file with the same name as the folder itself.

**Pattern:**

```
enforce/
  enforce.md      ← top-level instructions for the enforce folder
  ...

rules/
  rules.md        ← top-level instructions for the rules folder
  ...
```

This makes the entrypoint predictable: to understand any folder, read the `{folder-name}.md` inside it.

Never name the entrypoint `README.md`, `index.md`, or something generic — the folder name is the meaningful identifier.
