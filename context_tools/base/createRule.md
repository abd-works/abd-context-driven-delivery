# Create Rule

One action. Do not call this if **scan** already reports a failure that matches the mistake.

Take **failed** (what went wrong on the asset) and **wanted** (what should have happened). Using **contexts**, **examples**, and **template**, evaluate a new named rule and a matching scanner that can detect that failure deterministically.

Write the rule and the scanner into **this tool** (the context tool's own guidance and `scanners/`). Then **run that rule** via **scan** on the asset and **detect a failure that matches the mistake**. If scan is clean, or the failures are not this mistake, the rule/scanner is not done.
