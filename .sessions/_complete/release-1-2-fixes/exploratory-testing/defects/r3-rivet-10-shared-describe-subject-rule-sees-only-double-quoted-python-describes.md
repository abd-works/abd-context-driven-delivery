# The `shared-describe-subject` graph rule reports two top-level describes that share a subject only in a Python spec that writes them in double quotes; single-quoted Python and TypeScript specs pass

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Check Artifacts Against Rules"; no scenario covers this rule per format.
- **Module and class:** `cdd_guidance/practices/bdd/model/bdd_model.py` `BddModel.load_source_facts` (`_MAMBA_DESCRIBE = re.compile(r'^with description\("([^"]+)"\)', re.MULTILINE)` fills the fact `top_level_describes`), read by `cdd_guidance/practices/bdd/rules/shared_describe_subject.py` `SharedDescribeSubject.check`. The spec's Description nodes, which hold the same names for every language, are not used.
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`, calls in `drv\b4.json`).

1. `_trips/probe/shared_double_spec.py`:

        with description("a bare cart registered for checkout"):
            with it("should total its lines"):
                pass  # BDD: SIGNATURE

        with description("a bare cart with items registered for checkout"):
            with it("should total zero"):
                pass  # BDD: SIGNATURE

2. `_trips/probe/shared_single_spec.py`: the same with single quotes, the quoting `templates/bdd.py` itself uses (`with description('{DomainEntity}'):`).
3. `_trips/probe/shared.spec.ts`: the same two as top-level `describe("...", () => {` calls.
4. `validate.validate {"guidance": "bdd-behavior", "paths": [each file]}`

## Expected
All three reported (bdd.md `shared-describe-subject`: "Keep one outermost `describe` per domain subject"; the rule's globs name `**/*_spec.py` and `**/*spec.ts`).

## Actual
- Double quotes: "Spec `shared_double_spec`: Top-level describes 'a bare cart registered for checkout' and 'a bare cart with items registered for checkout' share subject 'a bare cart'; use one describe and nest ..."
- Single quotes: "No graph rule violations. All scanned graph rules passed." The checked graph holds the Spec with both Description nodes.
- TypeScript: the same, no violation, both Description nodes in the graph.

In the saved graph, the Spec nodes of the single-quoted Mamba specs in `src` hold no name in `top_level_describes`.

## Tier that should catch it
Unit: `shared_describe_subject_spec.py` uses double-quoted Python only.

## Also seen by
