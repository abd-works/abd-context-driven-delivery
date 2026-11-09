---
description: "Before committing a refactor or fix to this repository's code, run the metrics gate; a change that makes any code metric worse is not committed."
alwaysApply: true
---

# Metrics Gate

A refactor exists to make the code better. So before you commit a change to production code in `harness/`, `space/`, `tools/`, `cdd_guidance/` or `scripts/`, measure it against the commit it started from. Commit only when no metric got worse.

```
python .context/repo-review/metrics_gate.py --base <the commit your change started from> --head . --node-tools <folder with jscpd, dependency-cruiser and typescript>
```

Run it with the Python of a metrics venv that has radon, lizard, complexipy, cohesion, grimp and networkx installed. See `.context/repo-review/code-metrics-trend.md` for how to set one up.

**The gate fails when:**
- any of its metrics got worse, by any amount
- the change pushes any function, class or module past a limit
- the change makes anything already past a limit bigger

The gate names each offender, for example `harness/graph/graph.py:Graph._take` with 18 paths. A slow creep of one more complex function per change is how the code got worse in rounds 5 to 8, so a change of one counts.

**When the gate fails, fix the code, not the gate:**
- **A function grew past 10 paths, past a readability score of 15, or past 50 lines.** Split it into named steps.
- **A function takes more than 5 parameters.** Hold what it needs on its object.
- **A class grew past 100 total complexity or 30 methods.** Move a job into a part the class holds.
- **A class depends on more classes than before.** Ask a collaborator it already holds instead of reaching past it.
- **A class gained a group of methods sharing no data with the rest.** That group is a second job, so give it a class of its own.

Moving behaviour onto the class that owns the data is right. But if the owner then grows past these limits, split the owner into parts it holds; don't let it become one large class.

Report the gate's table in your report, so whoever merges your work sees what it did to the code. If a metric must get worse for a reason you can defend, such as a deliberate trade, say which metric and why. Then write that down in a decision record in the module's `.context/cdr/`, so the trade is a decision rather than drift.
