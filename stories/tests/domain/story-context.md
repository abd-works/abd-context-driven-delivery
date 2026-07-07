# story-context.md — Assemble Skill Components

**Source:** `stories/tests/spec_fidelity.py`, `spec_phase.py`, `spec_front_matter.py`,
`spec_skill.py`, `spec_loader.py`, `spec_cli.py`

**Layout:** documentation mode — reverse-engineered from mamba spec files

---

## Story Map

```
(E) Assemble Skill Components
    (E) Parse Fidelity Levels
        (S) Agent --> Resolve a fidelity level from a string value
        (S) Agent --> Detect an unrecognised fidelity string
    (E) Scope Files by Phase
        (S) Agent --> Scope to the correct directories for each phase
        (S) Agent --> Detect an unrecognised phase string
    (E) Match Files by Front Matter
        (S) Agent --> Match a file to a fidelity and format request
        (S) Agent --> Reject a file that does not match the request
    (E) Assemble a Manifest
        (S) Agent --> Include matching files and group by directory
        (S) Agent --> Exclude non-matching files
        (S) Agent --> Produce deterministic output ordering
    (E) Load Skill from Disk
        (S) Agent --> Load files with valid front matter
        (S) Agent --> Handle files with invalid or missing front matter
        (S) Agent --> Ignore files outside the known scope
    (E) Run Assembly Command
        (S) Agent --> Complete the assembly from CLI arguments
        (S) Agent --> Soft-fail and report anomalies
        (S) Agent --> Refuse an invalid request
```

---

## Thin Slices

### Increment 1: Parse and Validate Fidelity and Phase

**Outcome:** The system can interpret and validate the two core discriminators used in
every assembly request.

**Stories in this increment:**
- *Resolve a fidelity level from a string value*
- *Detect an unrecognised fidelity string*
- *Scope to the correct directories for each phase*
- *Detect an unrecognised phase string*

---

### Increment 2: Match and Filter by Front Matter

**Outcome:** Individual skill files can declare their own scope, and the system can decide
whether each file belongs in a given assembly request.

**Stories in this increment:**
- *Match a file to a fidelity and format request*
- *Reject a file that does not match the request*

---

### Increment 3: Assemble a Manifest in Memory

**Outcome:** A complete in-memory skill package can be assembled into a filtered, grouped,
ordered manifest.

**Stories in this increment:**
- *Include matching files and group by directory*
- *Exclude non-matching files*
- *Produce deterministic output ordering*

---

### Increment 4: Load Skill from Disk

**Outcome:** The assembler can read a real skill directory tree, parse front matter, and
soft-fail on malformed files without aborting.

**Stories in this increment:**
- *Load files with valid front matter*
- *Handle files with invalid or missing front matter*
- *Ignore files outside the known scope*

---

### Increment 5: Run Assembly via CLI

**Outcome:** The full assembly pipeline is accessible as a CLI command that emits
structured JSON and never fails silently.

**Stories in this increment:**
- *Complete the assembly from CLI arguments*
- *Soft-fail and report anomalies*
- *Refuse an invalid request*

---

## Story Details

### Parse Fidelity Levels

#### Story: Resolve a fidelity level from a string value

**Behaviors:**
- it should resolve to the matching level
- it should resolve to all five levels in that order

#### Story: Detect an unrecognised fidelity string

**Behaviors:**
- it should not be recognised as a valid level
- the error: it should carry the unrecognised string

#### Story: Return all levels in pipeline order

**Behaviors:**
- it should run from shaping through to engineering

---

### Scope Files by Phase

#### Story: Scope to the correct directories for each phase

**Behaviors:**
- it should include concepts and grill-me-questions only  (Interview)
- it should include templates, rules, behavior, and concepts  (Generate)
- it should include rules only  (Validate)

#### Story: Detect an unrecognised phase string

**Behaviors:**
- it should not be resolved

---

### Match Files by Front Matter

#### Story: Match a file to a fidelity and format request

**Behaviors:**
- it should match the request  (overlapping fidelity sets)
- it should match any requested format  (no format declared)
- it should match  (requested format matches declared format)

#### Story: Reject a file that does not match the request

**Behaviors:**
- it should not match the request  (non-overlapping fidelity sets)
- it should not match  (requested format differs from declared format)
- it should not match any request  (empty fidelity set)

---

### Assemble a Manifest

#### Story: Include matching files and group by directory

**Behaviors:**
- it should include files whose fidelity overlaps the requested set
- it should include files whose format matches or is absent
- it should group the included files by their directory
- it should include rules files only  (Validate phase)
- it should include the file  (multi-fidelity file, one level requested)

#### Story: Exclude non-matching files

**Behaviors:**
- it should exclude that file  (wrong format)
- it should exclude that file  (wrong fidelity)

#### Story: Produce deterministic output ordering

**Behaviors:**
- it should list them in deterministic path order

---

### Load Skill from Disk

#### Story: Load files with valid front matter

**Behaviors:**
- it should include every file
- it should record no anomalies
- the loaded front matter: it should carry the declared fidelities
- the loaded front matter: it should carry the declared format
- the loaded front matter: it should carry the declared section

#### Story: Handle files with invalid or missing front matter

**Behaviors:**
- it should still include the file with its valid fidelities only  (unrecognised fidelity value)
- the anomaly record: it should name the unrecognised value
- it should exclude that file  (missing front matter block)
- the anomaly record: it should identify the file as missing front matter

#### Story: Ignore files outside the known scope

**Behaviors:**
- it should ignore the file  (unrecognised directory)
- it should ignore the file  (non-markdown file in known directory)

---

### Run Assembly Command

#### Story: Complete the assembly from CLI arguments

**Behaviors:**
- it should complete the assembly
- it should emit a manifest on standard output as structured data
- it should emit nothing on standard error
- the manifest: it should list the requested phase
- the manifest: it should list the requested fidelities
- the manifest: it should group matched files by their directory

#### Story: Soft-fail and report anomalies

**Behaviors:**
- it should still complete the assembly
- it should emit the anomaly on standard error as structured data

#### Story: Refuse an invalid request

**Behaviors:**
- it should refuse the request
- it should emit a structured error on standard error
