---
description: Use {curly-braces} for placeholders in templates, not <angle-brackets>.
globs: **/*.md
---

All template placeholders must use `{curly-braces}`, not `<angle-brackets>`.

**Correct:** `{rule-name}`, `{domain}`, `{artifact-glob}`  
**Incorrect:** `<rule-name>`, `<domain>`, `<artifact-glob>`

Curly braces are unambiguous in markdown — angle brackets are reserved for HTML tags and cause rendering issues.
