# Agent Protocol — Practice Skills

Read this file when any practice skill tells you to. It defines the three conventions shared by all practice skills.

---

## Output file resolution (deliverables)

**Where to write deliverables (`<deliverables-folder>` resolution):**

1. **The path the user told you to use.** If the user names a file or folder, use exactly that.
2. **Where the engagement already keeps deliverables.** Look at the workspace; if previous phase output already lives in a folder, write next to them in the **same** folder.
3. **The workspace root.** If neither applies, write to the workspace root.
---

## Read-gates

Before authoring any artifact:

- Read every file in **`reference/`** for the active skill.
- Read every file in **`rules/`** for the active skill. Treat each DO / DO NOT as a hard contract — not a suggestion.

Do not rely on memory or the SKILL body alone.

---

## Per-rule verdict format (validation)

After generating, re-read every file in **`rules/`** for the active skill. For **each rule**, emit:

```
Rule: <rule-filename>  ->  PASS
Rule: <rule-filename>  ->  FAIL  <offending line or reason>
```

**No rule may be silently skipped.** Fix every FAIL and every scanner violation before calling the work done.
