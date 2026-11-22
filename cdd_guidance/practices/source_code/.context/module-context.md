# cdd_guidance/practices/source_code
Source code as several practices read it. *CodeBody* is an operation's body as it was read, in its *CodeLanguage* (`PYTHON`, `TYPESCRIPT`, `JAVASCRIPT`): rendered in the same language it comes back as written, rendered in another it comes back commented out above a statement that fails until someone writes it. *BracketStructure* says which bracket closes which in a brace-language span, and `split_top_level` splits a parameter list at its top-level commas. *CallGraph* is the `-> callee` arrows a document writes under a member. *ScriptImports* reads the classes a file imports, each a *ClassReference* with the module it names it from. *SourceText* is a span of source measured for the rules, with the parts it holds, *SpanFailures* and *SpanCollaborators*; it is one *MeasuredBody*, the measures every operation's body answers whichever way its parser read it. *TestFileName* and `is_test_code`, `is_spec_file`, `is_example_code` say which files are test code, specs, or examples.

It has the same standing as `sketch_document`: shared by practices, not a practice.

- **Purpose:** Let Stories, BDD, DDD, the patterns, and space/session read code without loading Clean Engineering's class model, so a brace is parsed by one reader and a test file is named by one rule.
- **Seam (terms):** CodeBody, CodeLanguage, CodeSpelling, BraceCall, WrittenBlock, WrittenKey, InsideLines, PYTHON, TYPESCRIPT, JAVASCRIPT, CODE_LANGUAGES, BracketStructure, split_top_level, CallGraph, CallGraphEntry, parse_arrow_line, ScriptImports, ClassReference, STAR, imported_files, MeasuredBody, SourceText, SpanFailures, SpanCollaborators, TestFileName, is_test_code, is_spec_file, is_example_code. Callers import them from the package (`from cdd_guidance.practices.source_code import CodeBody`).
- **Dependencies (one-way):** the standard library only. Nothing here imports a practice, a pattern, or the framework.

## Constraint

Code here reads text; it knows no practice's nodes and holds no rule. A measure a rule compares is written here only when more than one practice reads it; Clean Engineering's own measures stay in its `model/operation_metrics.py`.
