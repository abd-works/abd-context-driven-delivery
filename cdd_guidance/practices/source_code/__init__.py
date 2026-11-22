"""Source code as several practices read it: an operation's body in its language, the brackets of a brace-language span,
a call graph written in a document, the imports of a script, a span of source measured for the rules, and which files
are test code. It depends on nothing in the practices, so Stories, BDD, DDD, the patterns, and space/session read code
without loading Clean Engineering's class model."""

from cdd_guidance.practices.source_code.bracket_structure import BracketStructure, split_top_level
from cdd_guidance.practices.source_code.call_graph import CallGraph, CallGraphEntry, parse_arrow_line
from cdd_guidance.practices.source_code.code_body import (
    CODE_LANGUAGES,
    JAVASCRIPT,
    PYTHON,
    TYPESCRIPT,
    BraceCall,
    CodeBody,
    CodeLanguage,
    CodeSpelling,
    InsideLines,
    WrittenBlock,
    WrittenKey,
)
from cdd_guidance.practices.source_code.script_imports import STAR, ClassReference, ScriptImports, imported_files
from cdd_guidance.practices.source_code.source_text import MeasuredBody, SourceText, SpanCollaborators, SpanFailures
from cdd_guidance.practices.source_code.test_files import TestFileName, is_example_code, is_spec_file, is_test_code

__all__ = [
    "BraceCall",
    "BracketStructure",
    "CODE_LANGUAGES",
    "CallGraph",
    "CallGraphEntry",
    "ClassReference",
    "CodeBody",
    "CodeLanguage",
    "CodeSpelling",
    "InsideLines",
    "JAVASCRIPT",
    "MeasuredBody",
    "PYTHON",
    "STAR",
    "ScriptImports",
    "SourceText",
    "SpanCollaborators",
    "SpanFailures",
    "TYPESCRIPT",
    "TestFileName",
    "WrittenBlock",
    "WrittenKey",
    "imported_files",
    "is_example_code",
    "is_spec_file",
    "is_test_code",
    "parse_arrow_line",
    "split_top_level",
]
