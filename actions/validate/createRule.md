# Create Rule

One action. Do not call this if **validate** already reports a failure that matches the mistake. Do not call this to mint a ban-list rule for a one-off invented shape, or until you have checked that the existing **contexts**, **examples**, **template**, and generator/seed cannot steer the failure.

Take **failed** (what went wrong on the asset) and **wanted** (what should have happened). Using **contexts**, **examples**, and **template**, evaluate a new named rule and a CodeQL query that can detect that failure deterministically — only when the failure is mechanical and that existing surface cannot carry it.

Write the rule and the query into **this tool** (the context tool's own guidance and `codeql/`). Then **run collection validate** on the asset and **detect a failure that matches the mistake**. If validate is clean, or the failures are not this mistake, the rule/query is not done.
