# Domain Specification — Assemble Skill Components

## **Fidelity**

The five maturity levels at which skill content is tagged, ordered from least to most concrete.

### **Fidelity** << ValueObject >>
+ SHAPING: Fidelity
+ DISCOVERY: Fidelity
+ EXPLORATION: Fidelity
+ SPECIFICATION: Fidelity
+ ENGINEERING: Fidelity
---
+ parse(value: str): Fidelity
	Invariant: value must exactly match one of the five known strings
	Invariant: raises UnknownFidelityError when the value is not recognised
+ all(): tuple[Fidelity, ...]
	Invariant: returns all five levels in pipeline order shaping → engineering

### **UnknownFidelityError** : ValueError << ValueObject >>
+ value: str

---

## **Phase**

The workflow step that gates which directories are candidates for assembly.

### **Phase** << ValueObject >>
+ INTERVIEW: Phase
+ GENERATE: Phase
+ VALIDATE: Phase
---
+ parse(value: str): Phase
	Invariant: raises UnknownPhaseError when value is not one of the three known strings
+ directories(): tuple[str, ...]
	Invariant: INTERVIEW scopes to concepts and grill-me-questions only
	Invariant: GENERATE scopes to concepts, behavior, generate-instructions, templates, rules, examples
	Invariant: VALIDATE scopes to rules only

### **UnknownPhaseError** : ValueError << ValueObject >>
+ value: str

---

## **Anomaly**

A soft-fail signal emitted during loading or assembly. The run continues; anomalies are
reported alongside the manifest so the AI can surface them to the user.

### **Anomaly** << ValueObject >>
+ Anomaly(kind: str, file: str, details: dict[str, Any])
---
+ kind: str
+ file: str
+ details: dict[str, Any]
---
+ to_dict(): dict[str, Any]

---

## **FrontMatter**

The metadata parsed from the YAML block at the top of every skill file. Determines
whether the file is a candidate for a given assembly request.

### **FrontMatter** << ValueObject >>
+ FrontMatter(fidelities, format, section, artifact, scanner, raw)
---
+ fidelities: frozenset[Fidelity]
	Invariant: empty frozenset means the file matches no request
+ format: str | None
	Invariant: absent format is universal — matches any requested format
+ section: str | None
+ artifact: frozenset[str]
+ scanner: str | None
+ raw: dict[str, Any]
---
+ matches(fidelities: frozenset[Fidelity], format: str): bool
	Invariant: returns False when the fidelity sets do not intersect
	Invariant: returns False when format is declared and differs from the requested format
	Interaction:
		if self.fidelities ∩ fidelities is empty: return False
		if self.format is not None and self.format ≠ format: return False
		return True

---

## **SkillFile**

One file inside a skill package, addressed by its top-level directory and root-relative path.

### **SkillFile** << ValueObject >>
+ SkillFile(path: str, directory: str, front_matter: FrontMatter)
---
+ path: str
+ directory: str
	Invariant: must be one of the known top-level directories
+ << composition >> front_matter: FrontMatter
---
+ matches(fidelities: frozenset[Fidelity], format: str): bool
	Interaction:
		return self.front_matter.matches(fidelities, format)

---

## **Manifest**

The assembled result: skill files selected for a run, grouped by directory, with any
load anomalies attached.

### **Manifest** << ValueObject >>
+ Manifest(phase: Phase, fidelities: tuple[Fidelity], format: str, files_by_directory, anomalies)
---
+ phase: Phase
+ fidelities: tuple[Fidelity, ...]
	Invariant: ordered in pipeline order (shaping → engineering), not in request order
+ format: str
+ << composition >> files_by_directory: dict[str, tuple[SkillFile, ...]]
	Invariant: directories with no matched files are absent from the dict
+ << composition >> anomalies: tuple[Anomaly, ...]
---
+ files(): tuple[SkillFile, ...]
	Interaction:
		return flat tuple of all SkillFiles across every directory group
+ to_dict(): dict[str, Any]
	Interaction:
		emit phase as its string value
		emit fidelities as list of string values
		emit format as string
		emit files_by_directory as dict of directory → list of paths only

---

## **Skill**

Aggregate root. Holds all skill files loaded from disk and assembles them into a Manifest
on request.

### **Skill** << Entity >>
+ Skill(name: str, files: tuple[SkillFile], load_anomalies: tuple[Anomaly])
---
+ name: str
+ << composition >> files: tuple[SkillFile, ...]
+ << composition >> load_anomalies: tuple[Anomaly, ...]
	Invariant: anomalies accumulated during loading are carried through to every assembled Manifest
---
+ assemble(fidelities: frozenset[Fidelity], format: str, phase: Phase): Manifest
	Invariant: only files whose directory is in the phase scope are candidates
	Invariant: only files passing FrontMatter.matches are included
	Invariant: files within each directory are sorted by path for deterministic ordering
	Invariant: directories with no matched files are excluded from the result
	Interaction:
		scope: set[str] = phase.directories()
		matched: dict[str, list[SkillFile]] = {directory: [] for directory in scope}
		for each skillFile in self.files:
			if skillFile.directory not in scope: skip
			if not skillFile.matches(fidelities, format): skip
			matched[skillFile.directory].append(skillFile)
		sort each group by skillFile.path
		files_by_directory: dict = {directory: group for group if group is non-empty}
		orderedFidelities: tuple = fidelities in Fidelity.all() order
		return Manifest(phase, orderedFidelities, format, files_by_directory, self.load_anomalies)

---

## **Boundary — Filesystem Loader**

Adapter that reads a skill root directory tree and produces a Skill aggregate.

### **load_skill(skill_root: Path, name: str | None): Skill** << Service >>
	Invariant: only .md files in known directories are included
	Invariant: files without a front matter block produce a missing_front_matter Anomaly; file excluded
	Invariant: files with invalid YAML produce an invalid_yaml Anomaly; file excluded
	Invariant: front matter that parses to a non-mapping YAML value produces a front_matter_not_mapping Anomaly; file excluded
	Invariant: a fidelity value that is not a string or list produces a fidelity_not_list Anomaly; file included with no fidelities
	Invariant: unrecognised fidelity values produce an unknown_fidelity Anomaly; file included with valid fidelities only
	Invariant: non-markdown files are ignored silently
	Invariant: files in unknown directories are ignored silently
	Interaction:
		for each .md file under skill_root in sorted order:
			if file.suffix not in {".md"}: skip
			directory: str = first path component relative to skill_root
			if directory not in _KNOWN_DIRECTORIES: skip
			rawContents: str = file.read_text(encoding="utf-8")
			frontMatter: FrontMatter | None, fileAnomalies: list[Anomaly] = _parse_front_matter(relativePath, rawContents)
			collect fileAnomalies
			if frontMatter is None: skip
			append SkillFile(path, directory, frontMatter) to skillFiles
		return Skill(name or skill_root.name, tuple(skillFiles), tuple(anomalies))

---

## **Boundary — CLI**

Command-line entry point. Parses arguments, drives load + assemble, emits JSON.

### **main(argv: list[str] | None): int** << Boundary >>
	Invariant: exits with code 2 on any invalid argument before loading starts
	Invariant: structured error JSON is always emitted on stderr before a code-2 exit
	Invariant: emits manifest as JSON on stdout when assembly succeeds
	Invariant: emits anomaly payload on stderr when anomalies are present; run does not abort
	Interaction:
		fidelities: frozenset[Fidelity] = parse --fidelity (comma-separated list)
		if any fidelity is unrecognised: emit unknown_fidelity_argument error to stderr, return 2
		if fidelities is empty: emit empty_fidelity_argument error to stderr, return 2
		phase: Phase = parse --phase
		if skill_root path does not exist: emit skill_root_not_found error to stderr, return 2
		skill: Skill = load_skill(skill_root)
		manifest: Manifest = skill.assemble(fidelities, args.format, phase)
		json.dump(manifest.to_dict()) to stdout
		if manifest.anomalies: emit {anomalies: [...]} payload to stderr
		return 0

---

## **Boundary — Scanner Framework**

Base types that every rule scanner extends. Scanners consume a Workspace from the stories domain; this boundary defines the scanner contract and the CLI runner that wires it.

### **ArtifactKind** << ValueObject >>

The artifact kinds a scanner can declare it reads. Each value corresponds to a collection on Workspace.

Initialisation: predefined string constants
------
+ STORY_MAP: ArtifactKind
+ THIN_SLICE: ArtifactKind
+ SCENARIOS: ArtifactKind
+ TESTS: ArtifactKind

---

### **Violation** << ValueObject >>

One scanner finding — a rule breach at a specific file location.

+ Violation(rule: str, message: str, location: str, severity: str, hint: str | None)
------
+ rule: str
+ message: str
+ location: str
+ severity: str
	Invariant: defaults to "warning" when not explicitly supplied
+ hint: str | None
----
+ to_json(): str
	Interaction:
		emit dict of all non-None fields as a JSON string

---

### **ArtifactScanner** << Service >>

Abstract base every scanner subclasses. Subclasses set `rule`, `kind`, and `reads`, then implement `scan`.

+ ArtifactScanner(workspace: Workspace)
------
+ rule: str
+ kind: str
	Invariant: must be "shape" or "quality"
+ reads: tuple[ArtifactKind, ...]
	Invariant: defaults to ("story_map",) when not overridden
+ workspace: Workspace
----
+ scan(): Iterator[Violation]
	Invariant: subclasses must implement; base raises NotImplementedError
- location(source: Any, fallback: str): str
	Invariant: returns source.render() when source exposes a render method
	Invariant: returns fallback when source is None or render raises

---

### **run(scanner_cls: type): int** << Boundary >>

CLI runner shared by every scanner. Parses --workspace, loads the Workspace, runs the scanner, emits results.

	Invariant: exits with code 0 when no violations are found
	Invariant: exits with code 1 when one or more violations are found
	Invariant: exits with code 2 when the scanner raises an unexpected exception
	Invariant: each violation is emitted as a JSON line on stdout
	Invariant: a human-readable summary is emitted on stderr
	Interaction:
		root: Path = resolve --workspace argument (default ".")
		workspace: Workspace = load_workspace(root)
		scanner: ArtifactScanner = scanner_cls(workspace=workspace)
		violations: list[Violation] = list(scanner.scan())
		for each violation: print violation.to_json() to stdout
		print summary line to stderr
		return 0 if violations is empty else 1
