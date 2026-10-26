"""LERN tier facts — read once from tier files while the overlay records its nodes.

The recorder sets these on the NodeRoot, Route, Aggregate, Repository, and StoryShared nodes;
the LERN rules read them with ``get_fact`` and never open a file.
"""

from __future__ import annotations

import re
from pathlib import Path

_RAW_FILE_IO = re.compile(r"\b(?:readFileSync|writeFileSync)\s*\(")
_SCHEMA_PARSE = re.compile(r"(?<!JSON)\.(?:safe)?[pP]arse\s*\(")
_LOOSE_BODY_READ = re.compile(r"\breq\.body(?:\??\.\w+|\s*\[)|=\s*req\.body\b(?!\s*\?\?)")
_AD_HOC_THROW = re.compile(r"\bthrow\s*(?:\{|['\"`])")
_ERROR_STATUS_REPLY = re.compile(r"\bres\.status\(\s*[45]\d\d\s*\)\s*\.\s*(?:json|send)\s*\(")
_WEB_PATH = re.compile(r"""(['"`])(/(?!api/)[a-z][a-z0-9-]*(?:/[a-z0-9-]*)*)(?:\?[^'"`]*)?\1""")
_EXPORTED_INSTANCE = re.compile(r"export\s+const\s+(\w+)\s*=\s*new\s+(\w+)\s*\(")
_NODE_REPOSITORY_CLASS = re.compile(r"\bclass\s+(\w+RepositoryNode)\b[^{]*\{")
_ROUTE_REGISTRATION = re.compile(r"\b(?:router|app)\.(?:get|post|put|patch|delete|use|all)\(\s*$")
_CTX_CAST = re.compile(r"\bctx\.(\w+)\s+as\s+\w+")
_GIVEN_START = re.compile(r"\bgiven\s*\(\s*(['\"`])(.*?)\1\s*,")
_EXPECT = re.compile(r"\b(?:expect|assert)\s*\(")
_PATHS_MODULE_SUFFIX = "-paths.ts"
_TEST_SETUP_GLOBS = ("tests/**/vitest.setup.ts", "tests/**/repositories.ts", "tests/vitest.setup.ts")


def node_root_facts(text: str, setup_text: str) -> dict:
    """What a `-node.ts` file says about its node repositories and its errors."""
    repositories = _node_repository_bodies(text)
    return {
        "node_repositories": [
            {"name": name, "raw_io": _hits(_RAW_FILE_IO, body), "parses_on_read": bool(_SCHEMA_PARSE.search(body))}
            for name, body in repositories
        ],
        "unreset_instances": unreset_instances(text, [name for name, _body in repositories], setup_text),
        **error_handling_facts(text),
    }


def route_facts(text: str) -> dict:
    return {"loose_body_reads": _hits(_LOOSE_BODY_READ, text), **error_handling_facts(text)}


def error_handling_facts(text: str) -> dict:
    return {"ad_hoc_throws": _hits(_AD_HOC_THROW, text), "error_replies": _hits(_ERROR_STATUS_REPLY, text)}


def web_path_literals(root: Path, folder: str) -> list[list]:
    """[file, line, path] for each browser path written as a literal outside the aggregate's `*-paths.ts`."""
    found: list[list] = []
    for file in sorted((root / folder).glob("*.ts*")):
        if file.name.endswith(_PATHS_MODULE_SUFFIX):
            continue
        text = file.read_text(encoding="utf-8")
        relative = file.relative_to(root).as_posix()
        for match in _WEB_PATH.finditer(text):
            if _in_import(text, match.start()) or _ROUTE_REGISTRATION.search(text[max(0, match.start() - 40):match.start()]):
                continue
            found.append([relative, _line_of(text, match.start()), match.group(2)])
    return found


def unreset_instances(text: str, class_names: list[str], setup_text: str) -> list[list[str]]:
    """[instance, class] for each exported repository instance the test setup never resets."""
    missing: list[list[str]] = []
    for class_name in class_names:
        instance = _exported_instance(text, class_name)
        if instance is not None and not re.search(rf"\b{re.escape(instance)}\b", setup_text):
            missing.append([instance, class_name])
    return missing


def test_setup_text(root: Path) -> str:
    seen: set[Path] = set()
    parts: list[str] = []
    for pattern in _TEST_SETUP_GLOBS:
        for path in root.glob(pattern):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def story_shared_facts(text: str) -> dict:
    """Context casts and asserting Givens in a `*.story.shared.ts` file."""
    asserting = []
    for match in _GIVEN_START.finditer(text):
        body = _callback_body(text, match.end())
        if body is not None and _EXPECT.search(body):
            asserting.append([_line_of(text, match.start()), match.group(2)])
    return {
        "context_casts": [[_line_of(text, match.start()), match.group(0)] for match in _CTX_CAST.finditer(text)],
        "asserting_givens": asserting,
    }


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _hits(pattern: re.Pattern[str], text: str) -> list[list]:
    return [[_line_of(text, match.start()), match.group(0).strip()] for match in pattern.finditer(text)]


def _node_repository_bodies(text: str) -> list[tuple[str, str]]:
    """Each `class …RepositoryNode { … }` in the file, with its body."""
    found: list[tuple[str, str]] = []
    for match in _NODE_REPOSITORY_CLASS.finditer(text):
        body = _braced_body(text, match.end() - 1)
        if body is not None:
            found.append((match.group(1), body))
    return found


def _callback_body(text: str, start: int) -> str | None:
    """The `{ … }` body of the arrow function that starts at or after ``start``."""
    open_brace = text.find("{", start)
    arrow = text.find("=>", start)
    if open_brace == -1 or arrow == -1 or arrow > open_brace:
        return None
    return _braced_body(text, open_brace)


def _braced_body(text: str, open_brace: int) -> str | None:
    depth = 0
    for index in range(open_brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace + 1:index]
    return None


def _in_import(text: str, index: int) -> bool:
    line_start = text.rfind("\n", 0, index) + 1
    line_end = text.find("\n", index)
    line = text[line_start:line_end if line_end != -1 else len(text)]
    return line.lstrip().startswith(("import ", "export ")) and " from " in line


def _exported_instance(text: str, class_name: str) -> str | None:
    for match in _EXPORTED_INSTANCE.finditer(text):
        if match.group(2) == class_name:
            return match.group(1)
    return None
