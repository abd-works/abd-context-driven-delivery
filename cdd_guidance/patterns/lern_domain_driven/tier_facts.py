"""LERN tier facts — read once from tier files while the overlay records its nodes.

The recorder sets these on the NodeRoot, Route, Aggregate, Repository, and StoryShared nodes;
the LERN rules read them with ``get_fact`` and never open a file.
"""

from __future__ import annotations

import re
from pathlib import Path

_RAW_FILE_IO = re.compile(r"\b(?:readFileSync|writeFileSync)\s*\(")
_STORE_READ = re.compile(r"\b(?:readLowDb|readFileSync|JSONFilePreset|JSONFileSyncPreset)\s*\(")
_ANY_BODY_READ = re.compile(r"\breq\.body\b")
_ANY_REQUEST_READ = re.compile(r"\breq\.(?:body|query|params|headers|cookies)\b")
_JSON_PATH_CONSTANT = re.compile(r"\bconst\s+(\w+)\s*=[^;\n]*\.json['\"`]")
_MODULE_FUNCTION = re.compile(r"^(?:export\s+)?function\s+(\w+)\s*\(", re.MULTILINE)
_TOP_LEVEL_HELPER = re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(", re.M)
_TOP_LEVEL_END = re.compile(r"^\};?\s*$", re.M)
_DOMAIN_CALL = re.compile(r"\brepositories\.\w+(?:\.\w+)?")
_HAND_WRITTEN_ROW = re.compile(r"\bscenario\(\s*(['\"])(?P<outline>[^'\"]+?):\s+(?P<row>[^'\"]+)\1")
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
    """What a `-node.ts` file says about its store-reading repositories, posted-body reads, and errors."""
    store_readers = [
        (name, code)
        for name, body in _node_repository_bodies(text)
        if (code := _store_code(text, body)) is not None
    ]
    return {
        "node_repositories": [
            {"name": name, "raw_io": _hits(_RAW_FILE_IO, code), "parses_on_read": bool(_SCHEMA_PARSE.search(code))}
            for name, code in store_readers
        ],
        "unreset_instances": unreset_instances(text, [name for name, _code in store_readers], setup_text),
        "unparsed_body_reads": [
            _line_of(text, match.start()) for match in _ANY_BODY_READ.finditer(text) if not _inside_schema_parse(text, match.start())
        ],
        **error_handling_facts(text),
    }


def core_request_reads(root: Path, folder: str) -> list[list]:
    """[file, line, code] for each request read in the framework-free core `<folder>/<aggregate>.ts`."""
    core = root / folder / f"{Path(folder).name}.ts"
    if not core.is_file():
        return []
    text = core.read_text(encoding="utf-8")
    relative = core.relative_to(root).as_posix()
    return [[relative, _line_of(text, match.start()), match.group(0)] for match in _ANY_REQUEST_READ.finditer(text)]


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
            if _in_import(text, match.start()) or _in_comment(text, match.start()) or _ROUTE_REGISTRATION.search(text[max(0, match.start() - 40):match.start()]):
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
    from cdd_guidance.patterns.lern_domain_driven.lern_domain_driven import LernDomainDriven

    seen: set[Path] = set()
    parts: list[str] = []
    for pattern in (*_TEST_SETUP_GLOBS, f"{LernDomainDriven.story_test_folder}/repositories.ts"):
        for path in root.glob(pattern):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def story_file_facts(text: str) -> dict:
    """What a LERN story file (shared, server, domain, or playwright) says about its steps and helpers."""
    asserting = []
    for match in _GIVEN_START.finditer(text):
        body = _callback_body(text, match.end())
        if body is not None and _EXPECT.search(body):
            asserting.append([_line_of(text, match.start()), match.group(2)])
    return {
        "context_casts": [[_line_of(text, match.start()), match.group(0)] for match in _CTX_CAST.finditer(text)],
        "asserting_givens": asserting,
        "domain_wrapping_helpers": _domain_wrapping_helpers(text),
        "hand_written_rows": [
            [_line_of(text, match.start()), match.group("outline"), match.group("row")]
            for match in _HAND_WRITTEN_ROW.finditer(text)
        ],
    }


def _domain_wrapping_helpers(text: str) -> list[list]:
    """[line, helper, repository calls] for each top-level helper that reaches the repositories."""
    found: list[list] = []
    for match in _TOP_LEVEL_HELPER.finditer(text):
        end = _TOP_LEVEL_END.search(text, match.end())
        calls = sorted(set(_DOMAIN_CALL.findall(text[match.end():end.start() if end else len(text)])))
        if calls:
            found.append([_line_of(text, match.start()), match.group(1) or match.group(2), calls])
    return found


def _store_code(text: str, class_body: str) -> str | None:
    """The code a node repository reads its store with: its body plus the same-file functions it calls.

    None when the class never touches a store, as with a wrapper that delegates to another repository.
    """
    path_names = _JSON_PATH_CONSTANT.findall(text)
    helpers = {
        match.group(1): body
        for match in _MODULE_FUNCTION.finditer(text)
        if (body := _braced_body(text, text.find("{", match.end()))) is not None
    }
    called = [body for name, body in helpers.items() if re.search(rf"\b{re.escape(name)}\s*\(", class_body)]
    code = "\n".join([class_body, *called])
    touches_store = _STORE_READ.search(code) or any(re.search(rf"\b{re.escape(name)}\b", code) for name in path_names)
    return code if touches_store else None


def _inside_schema_parse(text: str, index: int) -> bool:
    """True when this `req.body` is an argument of a `.parse(` / `.safeParse(` call that is still open."""
    statement_start = max(text.rfind(";", 0, index), text.rfind("{\n", 0, index), text.rfind("=>", 0, index))
    before = text[statement_start + 1:index]
    call = _SCHEMA_PARSE.search(before)
    if call is None:
        return False
    opened = before[call.end():]
    return opened.count("(") + 1 > opened.count(")")


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
    if open_brace < 0:
        return None
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


def _in_comment(text: str, index: int) -> bool:
    """A path a doc or line comment names is prose, not a literal the code uses."""
    line_start = text.rfind("\n", 0, index) + 1
    if re.search(r"(?:^|\s)//", text[line_start:index]):
        return True
    opened = text.rfind("/*", 0, index)
    return opened != -1 and text.find("*/", opened, index) == -1


def _exported_instance(text: str, class_name: str) -> str | None:
    for match in _EXPORTED_INSTANCE.finditer(text):
        if match.group(2) == class_name:
            return match.group(1)
    return None
