Read and apply the rules against an artifact — all rules or a single rule `<rule-name>`.

`rules/` always refers to the `rules/` sub-folder of the capability being validated.

- [ ] Read `rules/<rule-name>/<rule-name>.md` **in full** — no skimming, no summarising from memory.
- [ ] Read every file in `rules/<rule-name>/examples/pass/` and `rules/<rule-name>/examples/fail/` **in full**.
- [ ] Taking the role of an adversarial reviewer, validate the artifact **by intent** — every **DO**, **DO NOT**, and example is part of the contract.
- [ ] Emit one verdict per rule: `Rule: <rule-name>  ->  PASS` or `FAIL  <reason>`.
