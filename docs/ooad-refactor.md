
alysis of six concrete duplications and contradictions across abd-clean-code, the five ACE skills, and the five DDD skills — plus one recommendation with a three-commit execution plan.

Every finding is checkable with grep and diff against the current repo.

Findings
F1 — Nine rule filenames are duplicated between abd-domain-model/rules/ and abd-domain-specification/rules/; diff shows all nine have drifted. Concrete: dependency-magnet-split-concerns.md in the model skill uses a collaborator count (5–7); the copy in the spec skill uses a "business concerns" criterion. Same name, different rule.
F2 — Single-responsibility is authored in four separate rule files across DDD (twice), ACE (package-surface-is-cohesive), and clean-code (keep-classes-single-responsibility) — four different check criteria, four different examples, zero cross-references.
F3 — Direct contradiction: abd-domain-model/reference/concepts.md § What this format omits forbids << stereotypes >>; abd-architecture-specification/templates/mechanism-context.md § Class Specification requires ## ClassName << Stereotype >>. DDD's own rule and ACE's own template disagree.
F4 — Three different class-notation formats for the same modelling task (DDD model, DDD spec, ACE mechanism-context) — including two different visibility conventions (+/- vs - only).
F5 — stages/engineering/abd-clean-code/templates/clean-code.py (concrete Cart/Order classes) and practices/domain-driven-design/skills/abd-domain-model/templates/domain-model.py (abstract KaName) both produce Python domain modules with overlapping scope and no compositional contract, despite abd-domain-code officially delegating to abd-clean-code.
F6 — DDD's anti-example class is literally called BoardManager, which clean-code's use-domain-language.md forbids explicitly.
Root cause
Every finding is one problem in disguise: class-scale OOAD — rules, notation, templates — is authored per skill, not per library. DDD authored oo-concepts.md but only wired it into its own skills. ACE re-authored the same substrate in a template. Clean-code re-authored the same rules with its own examples. Within DDD, the model and spec skills authored parallel copies of the same nine rules and let them drift.

Recommendation
One move, three commits — no options menu:

Create common/reference/class-design.md + class-block-format.md — the shared class-scale substrate (naming, cohesion, encapsulation, DI, notation). Resolve the DDD-vs-ACE stereotype contradiction here in one call.
Rewire the four skills — clean-code, ACE spec, DDD model, DDD spec — to cite the shared substrate. Their rule files shrink to short scale-specific specialisations.
Collapse the intra-DDD duplication — for each of the nine F1 rule pairs, keep one canonical text and delete the duplicate; the other skill links to it.
Estimated: one new folder, ~25 file edits, ~9 file deletes.

