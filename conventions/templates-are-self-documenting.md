---
description: Every template must contain instructions on how to use it.
globs: **/{*-template*,template*,{*}*}.md
---

Every template file must open with a comment block that tells the author exactly what to do — steps, structure, and any naming conventions — so the template is self-documenting without needing an external guide.

**Pattern:**

```
<!--
HOW TO USE THIS TEMPLATE
========================
1. {First step}
2. {Second step}
...

Structure:
  {folder}/
    {file}    ← description
-->
```

A template without usage instructions requires the author to look elsewhere. Put the instructions where they will actually be read — at the top of the template itself.
