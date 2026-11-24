# space/session/practices

What each practice and fidelity has in a session, and the guidance selection a page shows: the session's core makes these and holds them.

- **Purpose:** Keep what each practice and each of its fidelities has in one session, where it writes, which files it declares and holds there, and the guidance selection a page shows and acts on.
- **Seam (terms):** PracticeSessionOutput, FidelitySessionOutput, WrittenFiles, ProposedRoots, SessionPractices, GuidanceSelection, FileListing, OutputRootRefused
- **Dependencies (one-way):** space/session/files, space/session/validation, harness/process, harness/guidance, harness/agent_tools, harness/installation, harness/mcp, harness/markdown, harness/design_canvas, harness/whiteboard

## PracticeSessionOutput

What one practice has in one session: the session's one instance of the practice, whether it is on, and the folder it writes under.

+ PracticeSessionOutput(guidance: PracticeGuidance, session: Session)
------
+ name: str
+ << association >> session: Session
+ session_file: str
+ << composition >> guidance: PracticeGuidance
+ fidelities: GuidanceCollection
+ fields: PracticeFields
+ enabled: bool
+ folder: Path
+ output_root: Path
+ root: str
+ is_root_chosen: bool
----
+ load(session: str, practice: str, call: ToolCall): PracticeSessionOutput
	-> ToolCall.session_named
	-> Session.practice
+ of_fidelity(fidelity: FidelityGuidance): FidelitySessionOutput
+ change(change: Callable[[PracticeFields], object], said: str): None
+ enable(is_enabled: bool): PracticeSessionOutput
+ choose_root(path: str): PracticeSessionOutput
+ root_named(path: str): Path
	// an empty path, a path to a file, and a folder outside the project raise OutputRootRefused; a folder that is not there yet is a root the practice writes into
+ keep_root(root: Path): None
+ use_default_root(): PracticeSessionOutput
---<<creates>>--> FidelitySessionOutput
---<<reads the configured folder from>>--> ContextConfig
---<<saves fields>>--> Session
---<<raises>>--> OutputRootRefused
---<<annotated with>>--> Identity
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> NoSessionLog

## FidelitySessionOutput

Where one fidelity writes in one session: its output paths by format, the files it declares there, the format it last used, and its reports folder.

+ FidelitySessionOutput(practice: PracticeSessionOutput, fidelity: FidelityGuidance)
------
+ << association >> practice: PracticeSessionOutput
+ << association >> fidelity: FidelityGuidance
+ is_enabled: bool
+ reports_folder: Path
+ root: Path
+ root_paths: list[str]
+ chosen_formats: list[str]
+ fields: FidelityFields
+ << composition >> formats: FidelityFormats
+ << composition >> validation_reports: ValidationReports
+ << composition >> written: WrittenFiles
----
+ load(session: str, practice: str, fidelity: str, call: ToolCall): FidelitySessionOutput
+ choose_root(path: str): FidelitySessionOutput
+ add_root(path: str): FidelitySessionOutput
+ keep_roots(roots: list[Path]): None
+ choose_format(format: str, is_chosen: bool): FidelitySessionOutput
---<<holds>>--> WrittenFiles

## WrittenFiles

The files one fidelity writes in a session (`session_output.written`): where it writes each format under its root, the files it declares there, whether any is there yet, and which the session's branch changed.

+ WrittenFiles(output: FidelitySessionOutput)
------
----
+ output_paths(): dict[str, list[str]]
+ saved_beside(source: Path, format: str): Path | None
	// the file DeclaredOutputs.file_beside places for source, under the root of this fidelity that holds it
+ files_to_review(): dict[str, list[FileEntry]]
+ files(): dict[str, list[FileEntry]]
	-> SessionFiles.find
+ holds(file: Path): bool
+ every_file(): list[Path]
+ has_output(): bool
+ has_named_output(): bool
+ has_found_output(): bool
---<<matches declared paths with>>--> DeclaredFile
---<<lists the declared files as>>--> FileEntry

## OutputRootRefused : ValueError

A path was chosen as the root a practice or a fidelity writes under that names no folder of the project: an empty path, a file, or a folder outside the project.

+ OutputRootRefused(path: str, reason: str)
------
+ path: str
----
