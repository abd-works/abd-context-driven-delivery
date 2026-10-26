"""LERN tier rules that read file text: node repositories, routes, web paths, and the test reset."""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.practice_rule import PracticeGraphRule

_RAW_FILE_IO = re.compile(r"\b(?:readFileSync|writeFileSync)\s*\(")
_STORE_READ = re.compile(r"\b(?:readLowDb|readFileSync|JSONFilePreset|JSONFileSyncPreset)\s*\(")
_ANY_BODY_READ = re.compile(r"\breq\.body\b")
_ANY_REQUEST_READ = re.compile(r"\breq\.(?:body|query|params|headers|cookies)\b")
_SCHEMA_PARSE = re.compile(r"(?<!JSON)\.(?:safe)?[pP]arse\s*\(")
_LOOSE_BODY_READ = re.compile(r"\breq\.body(?:\??\.\w+|\s*\[)|=\s*req\.body\b(?!\s*\?\?)")
_AD_HOC_THROW = re.compile(r"\bthrow\s*(?:\{|['\"`])")
_ERROR_STATUS_REPLY = re.compile(r"\bres\.status\(\s*[45]\d\d\s*\)\s*\.\s*(?:json|send)\s*\(")
_WEB_PATH = re.compile(r"""(['"`])(/(?!api/)[a-z][a-z0-9-]*(?:/[a-z0-9-]*)*)(?:\?[^'"`]*)?\1""")
_EXPORTED_INSTANCE = re.compile(r"export\s+const\s+(\w+)\s*=\s*new\s+(\w+)\s*\(")
_NODE_REPOSITORY_CLASS = re.compile(r"\bclass\s+(\w+RepositoryNode)\b[^{]*\{")
_ROUTE_REGISTRATION = re.compile(r"\b(?:router|app)\.(?:get|post|put|patch|delete|use|all)\(\s*$")
_PATHS_MODULE_SUFFIX = "-paths.ts"
_TEST_SETUP_GLOBS = ("tests/**/vitest.setup.ts", "tests/**/repositories.ts", "tests/vitest.setup.ts")


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _hits(pattern: re.Pattern[str], text: str) -> list[tuple[int, str]]:
    return [(_line_of(text, match.start()), match.group(0)) for match in pattern.finditer(text)]


class NodeRepositoryParsesOnRead(PracticeGraphRule):
    """`{Domain}RepositoryNode` reads its store through Zod and the lowdb helpers, never raw file IO.

    Checked on the `-node.ts` file: node repositories are not tactical Repository nodes in the graph.
    """

    slug = "node-repository-parses-on-read"
    node_types = ("NodeRoot",)

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        messages: list[str] = []
        for name, body in _node_repository_bodies(text):
            store_code = _store_code(text, body)
            if store_code is None:
                continue
            messages += [
                f"{name} line {line}: `{found.strip()}` reads or writes the store by hand; use the lowdb helpers."
                for line, found in _hits(_RAW_FILE_IO, store_code)
            ]
            if not _SCHEMA_PARSE.search(store_code):
                messages.append(f"{name} never runs a Zod `.parse(` on what it reads from its JSON store.")
        return messages


class PostedBodyParsedInNode(PracticeGraphRule):
    """The posted body is read once, in the node, through a Zod schema.

    A route hands `req` to `{Domain}Node.fromRequest`. A node passes `req.body` straight into a schema
    `.parse(` / `.safeParse(`. The framework-free core (`<aggregate>.ts`) never touches the request.
    """

    slug = "posted-body-parsed-in-node"
    node_types = ("Route", "NodeRoot", "Aggregate")

    def check(self, node, context) -> list[str]:
        if node.type == "Aggregate":
            return _core_request_reads(node, context)
        text = context.text(node)
        if node.type == "NodeRoot":
            return [
                f"{node.source.file}:{_line_of(text, match.start())}: `req.body` is read without a schema; "
                f"pass it straight into the posted schema's `.parse(`."
                for match in _ANY_BODY_READ.finditer(text)
                if not _inside_schema_parse(text, match.start())
            ]
        return [
            f"{node.source.file}:{line}: `{found}` reads the posted body loosely; pass `req` to the node's `fromRequest`, which parses it."
            for line, found in _hits(_LOOSE_BODY_READ, text)
        ]


class ThrowHttpExceptions(PracticeGraphRule):
    """Routes and nodes fail with `HttpException`; one error middleware turns it into the reply."""

    slug = "throw-http-exceptions"
    node_types = ("Route", "NodeRoot")

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        messages = [
            f"{node.source.file}:{line}: `{found.strip()}` throws an ad hoc value; throw an `HttpException`."
            for line, found in _hits(_AD_HOC_THROW, text)
        ]
        messages += [
            f"{node.source.file}:{line}: `{found.strip()}` answers an error by hand; throw an `HttpException` for the error middleware."
            for line, found in _hits(_ERROR_STATUS_REPLY, text)
        ]
        return messages


class OneHomeForWebPaths(PracticeGraphRule):
    """Browser paths are string literals in one `*-paths.ts` module; every other file imports them."""

    slug = "one-home-for-web-paths"
    node_types = ("Aggregate",)

    def check(self, node, context) -> list[str]:
        root = context.source_root
        folder = node.source.file.replace("\\", "/") if node.source.file else ""
        if root is None or not folder:
            return []
        messages: list[str] = []
        for file in sorted((root / folder).glob("*.ts*")):
            if file.name.endswith(_PATHS_MODULE_SUFFIX):
                continue
            text = file.read_text(encoding="utf-8")
            relative = file.relative_to(root).as_posix()
            for match in _WEB_PATH.finditer(text):
                if _in_import(text, match.start()) or _ROUTE_REGISTRATION.search(text[max(0, match.start() - 40):match.start()]):
                    continue
                messages.append(
                    f"{relative}:{_line_of(text, match.start())}: web path {match.group(2)!r} is a literal; "
                    f"import it from the aggregate's `*{_PATHS_MODULE_SUFFIX}` module."
                )
        return messages


class ResetEveryRepository(PracticeGraphRule):
    """Every exported repository instance is reset by the test setup, so no story sees another's state.

    In-memory repositories are checked on their Repository node, node repositories on the `-node.ts` file.
    """

    slug = "reset-every-repository"
    node_types = ("Repository", "NodeRoot")

    def check(self, node, context) -> list[str]:
        root = context.source_root
        if root is None:
            return []
        text = context.text(node)
        if node.type == "NodeRoot":
            classes = [name for name, body in _node_repository_bodies(text) if _store_code(text, body) is not None]
        else:
            classes = [node.name]
        setup_text = _test_setup_text(root)
        messages: list[str] = []
        for class_name in classes:
            instance = _exported_instance(text, class_name)
            if instance is None or re.search(rf"\b{re.escape(instance)}\b", setup_text):
                continue
            messages.append(f"`{instance}` ({class_name}) is never reset by the test setup; add it to the repositories every story resets.")
        return messages


def _node_repository_bodies(text: str) -> list[tuple[str, str]]:
    """Each `class …RepositoryNode { … }` in the file, with its body."""
    found: list[tuple[str, str]] = []
    for match in _NODE_REPOSITORY_CLASS.finditer(text):
        depth = 0
        for index in range(match.end() - 1, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    found.append((match.group(1), text[match.end():index]))
                    break
    return found


_JSON_PATH_CONSTANT = re.compile(r"\bconst\s+(\w+)\s*=[^;\n]*\.json['\"`]")
_MODULE_FUNCTION = re.compile(r"^(?:export\s+)?function\s+(\w+)\s*\(", re.MULTILINE)


def _store_code(text: str, class_body: str) -> str | None:
    """The code a node repository reads its store with: its body plus the same-file functions it calls.

    None when the class never touches a store, as with a wrapper that delegates to another repository.
    """
    path_names = _JSON_PATH_CONSTANT.findall(text)
    helpers = {name: body for name, body in _module_function_bodies(text)}
    called = [body for name, body in helpers.items() if re.search(rf"\b{re.escape(name)}\s*\(", class_body)]
    code = "\n".join([class_body, *called])
    touches_store = _STORE_READ.search(code) or any(re.search(rf"\b{re.escape(name)}\b", code) for name in path_names)
    return code if touches_store else None


def _module_function_bodies(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for match in _MODULE_FUNCTION.finditer(text):
        body = _braced_body(text, match.end())
        if body is not None:
            found.append((match.group(1), body))
    return found


def _braced_body(text: str, start: int) -> str | None:
    open_brace = text.find("{", start)
    if open_brace == -1:
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


def _inside_schema_parse(text: str, index: int) -> bool:
    """True when this `req.body` is an argument of a `.parse(` / `.safeParse(` call that is still open."""
    statement_start = max(text.rfind(";", 0, index), text.rfind("{\n", 0, index), text.rfind("=>", 0, index))
    before = text[statement_start + 1:index]
    call = _SCHEMA_PARSE.search(before)
    if call is None:
        return False
    opened = before[call.end():]
    return opened.count("(") + 1 > opened.count(")")


def _core_request_reads(node, context) -> list[str]:
    root = context.source_root
    folder = node.source.file.replace("\\", "/") if node.source.file else ""
    if root is None or not folder:
        return []
    core = root / folder / f"{Path(folder).name}.ts"
    if not core.is_file():
        return []
    text = core.read_text(encoding="utf-8")
    relative = core.relative_to(root).as_posix()
    return [
        f"{relative}:{_line_of(text, match.start())}: `{match.group(0)}` in the framework-free core; "
        f"the node reads the request and hands the core plain values."
        for match in _ANY_REQUEST_READ.finditer(text)
    ]


def _in_import(text: str, index: int) -> bool:
    line_start = text.rfind("\n", 0, index) + 1
    line = text[line_start:text.find("\n", index) if text.find("\n", index) != -1 else len(text)]
    return line.lstrip().startswith(("import ", "export ")) and " from " in line


def _exported_instance(text: str, class_name: str) -> str | None:
    for match in _EXPORTED_INSTANCE.finditer(text):
        if match.group(2) == class_name:
            return match.group(1)
    return None


def _test_setup_text(root: Path) -> str:
    seen: set[Path] = set()
    parts: list[str] = []
    for pattern in _TEST_SETUP_GLOBS:
        for path in root.glob(pattern):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)
