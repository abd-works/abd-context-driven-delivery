"""LERN fact files — each LERN file the overlay reads once while it records its nodes, as the kind of file it is.

A NodeRoot file, a Route file, a behavior file, and a story test file each say which node they become and the facts
they carry on it; an aggregate's folder gives the facts of the aggregate as a whole. The LERN rules read them with
``get_fact`` under the names in ``fact_names`` and never open a file.
"""

from __future__ import annotations

import re
from pathlib import Path

from cdd_guidance.patterns.fact_file import FactFile
from cdd_guidance.patterns.lern_domain_driven import fact_names
from cdd_guidance.practices.source_code import SourceText

_RAW_FILE_IO = re.compile(r"\b(?:readFileSync|writeFileSync)\s*\(")
_STORE_READ = re.compile(r"\b(?:readLowDb|readFileSync|JSONFilePreset|JSONFileSyncPreset)\s*\(")
_ANY_BODY_READ = re.compile(r"\breq\.body\b")
_ANY_REQUEST_READ = re.compile(r"\breq\.(?:body|query|params|headers|cookies)\b")
_JSON_PATH_CONSTANT = re.compile(r"\bconst\s+(\w+)\s*=[^;\n]*\.json['\"`]")
_MODULE_FUNCTION = re.compile(r"^(?:export\s+)?function\s+(\w+)\s*\(", re.MULTILINE)
_TOP_LEVEL_HELPER = re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(", re.M)
_TOP_LEVEL_END = re.compile(r"^\};?\s*$", re.M)
_DOMAIN_CALL = re.compile(r"\brepositories\.\w+(?:\.\w+)?")
_HAND_WRITTEN_ENTRY = re.compile(r"\bscenario\(\s*(['\"])(?P<outline>[^'\"]+?):\s+(?P<entry>[^'\"]+)\1")
_SCHEMA_PARSE = re.compile(r"(?<!JSON)\.(?:safe)?[pP]arse\s*\(")
_LOOSE_BODY_READ = re.compile(r"\breq\.body(?:\??\.\w+|\s*\[)|=\s*req\.body\b(?!\s*\?\?)")
_AD_HOC_THROW = re.compile(r"\bthrow\s*(?:\{|['\"`])")
_ERROR_STATUS_REPLY = re.compile(r"\bres\.status\(\s*[45]\d\d\s*\)\s*\.\s*(?:json|send)\s*\(")
_WEB_PATH = re.compile(r"""(['"`])(/(?!api\b)[a-z][a-z0-9-]*(?:/[a-z0-9-]*)*)(?:\?[^'"`]*)?\1""")
_EXPORTED_INSTANCE = re.compile(r"export\s+const\s+(\w+)\s*=\s*new\s+(\w+)\s*\(")
_NODE_REPOSITORY_CLASS = re.compile(r"\bclass\s+(\w+RepositoryNode)\b[^{]*\{")
# An API path is the server's address, not a browser page: a route registers it and an API client calls it.
_ROUTE_REGISTRATION = re.compile(r"\b(?:routes?|router|app|api)\.(?:get|post|put|patch|delete|use|all)(?:<[^>]*>)?\(\s*$")
# How far before a path literal a route registration may start and still be the call the path is passed to.
_ROUTE_CALL_REACH = 40
_CTX_CAST = re.compile(r"\bctx\.(\w+)\s+as\s+\w+")
_GIVEN_START = re.compile(r"\bgiven\s*\(\s*(['\"`])(.*?)\1\s*,")
_EXPECT = re.compile(r"\b(?:expect|assert)\s*\(")
_TIER_REACH = re.compile(r"""from\s+['"][^'"]*-(?:node|client|routes)['"]|\bpage\.\w+\(|\bfetch\(|\bsupertest\b""")
_RUNS_SHARED = re.compile(r"\bitBehavesLike\(")
_STUB = re.compile(r"\bvi\.(?:mock|fn|spyOn|stubGlobal)\(|\bjest\.(?:mock|fn|spyOn)\(")
_STUBBED_REQUEST = re.compile(r"\bpage\.route\(|\bcontext\.route\(")
_PATHS_MODULE_SUFFIX = "-paths.ts"


# A describe block, `test.describe('Add Child Ticket', …)`: in a screen story file, the story it drives.
_DESCRIBED = re.compile(r"""(?:test\.)?describe\(\s*(['"`])(.+?)\1""")

class LernFile(FactFile):
    """One LERN TypeScript file read once, with what every kind of LERN file can say about itself: the errors it
    answers, the requests it reads, the browser paths it writes, and the repository instances it exports. Its text is
    wrapped once however many facts are read from it."""

    def error_handling_facts(self) -> dict:
        return {fact_names.AD_HOC_THROWS: self._source.hits(_AD_HOC_THROW), fact_names.ERROR_REPLIES: self._source.hits(_ERROR_STATUS_REPLY)}

    def request_reads(self) -> list[list]:
        """[file, line, code] for each request read in this file."""
        return [[self.relative, self._source.line_of(match.start()), match.group(0)] for match in _ANY_REQUEST_READ.finditer(self._source.text)]

    def web_path_literals(self) -> list[list]:
        """[file, line, path] for each browser path this file writes as a literal: not in an import or a comment, and
        not an API path a route registers."""
        text = self._source.text
        found: list[list] = []
        for match in _WEB_PATH.finditer(text):
            if self._in_import(match.start()) or self._in_comment(match.start()) or _ROUTE_REGISTRATION.search(text[max(0, match.start() - _ROUTE_CALL_REACH):match.start()]):
                continue
            found.append([self.relative, self._source.line_of(match.start()), match.group(2)])
        return found

    def unreset_instances(self, class_names: list[str], setup_text: str) -> list[list[str]]:
        """[instance, class] for each exported repository instance of this file the test setup never resets."""
        missing: list[list[str]] = []
        for class_name in class_names:
            instance = self._exported_instance(class_name)
            if instance is not None and not re.search(rf"\b{re.escape(instance)}\b", setup_text):
                missing.append([instance, class_name])
        return missing

    def _store_code(self, class_body: str) -> str | None:
        """The code a node repository reads its store with: its body plus the same-file functions it calls.

        None when the class never touches a store, as with a wrapper that delegates to another repository.
        """
        text = self._source.text
        path_names = _JSON_PATH_CONSTANT.findall(text)
        helpers = {
            match.group(1): body
            for match in _MODULE_FUNCTION.finditer(text)
            if (body := self._braced_body(text.find("{", match.end()))) is not None
        }
        called = [body for name, body in helpers.items() if re.search(rf"\b{re.escape(name)}\s*\(", class_body)]
        code = "\n".join([class_body, *called])
        touches_store = _STORE_READ.search(code) or any(re.search(rf"\b{re.escape(name)}\b", code) for name in path_names)
        return code if touches_store else None

    def _inside_schema_parse(self, index: int) -> bool:
        """True when this `req.body` is an argument of a `.parse(` / `.safeParse(` call that is still open."""
        text = self._source.text
        statement_start = max(text.rfind(";", 0, index), text.rfind("{\n", 0, index), text.rfind("=>", 0, index))
        before = text[statement_start + 1:index]
        call = _SCHEMA_PARSE.search(before)
        if call is None:
            return False
        opened = before[call.end():]
        return opened.count("(") + 1 > opened.count(")")

    def _node_repository_bodies(self) -> list[tuple[str, str]]:
        """Each `class …RepositoryNode { … }` in the file, with its body."""
        text = self._source.text
        found: list[tuple[str, str]] = []
        for match in _NODE_REPOSITORY_CLASS.finditer(text):
            body = self._braced_body(match.end() - 1)
            if body is not None:
                found.append((match.group(1), body))
        return found

    def _callback_body(self, start: int) -> str | None:
        """The `{ … }` body of the arrow function that starts at or after ``start``."""
        text = self._source.text
        open_brace = text.find("{", start)
        arrow = text.find("=>", start)
        if open_brace == -1 or arrow == -1 or arrow > open_brace:
            return None
        return self._braced_body(open_brace)

    def _braced_body(self, open_brace: int) -> str | None:
        """The text between the brace at open_brace and the brace that closes it; none when it never closes."""
        text = self._source.text
        if open_brace < 0:
            return None
        depth = 0
        for index in range(open_brace, len(text)):
            depth += {"{": 1, "}": -1}.get(text[index], 0)
            if depth == 0:
                return text[open_brace + 1:index]
        return None

    def _in_import(self, index: int) -> bool:
        text = self._source.text
        line_start = text.rfind("\n", 0, index) + 1
        line_end = text.find("\n", index)
        line = text[line_start:line_end if line_end != -1 else len(text)]
        return line.lstrip().startswith(("import ", "export ")) and " from " in line

    def _in_comment(self, index: int) -> bool:
        """A path a doc or line comment names is prose, not a literal the code uses."""
        text = self._source.text
        line_start = text.rfind("\n", 0, index) + 1
        if re.search(r"(?:^|\s)//", text[line_start:index]):
            return True
        opened = text.rfind("/*", 0, index)
        return opened != -1 and text.find("*/", opened, index) == -1

    def _exported_instance(self, class_name: str) -> str | None:
        text = self._source.text
        for match in _EXPORTED_INSTANCE.finditer(text):
            if match.group(2) == class_name:
                return match.group(1)
        return None

class NodeRootFile(LernFile):
    """An aggregate's `-node.ts` file: its store-reading repositories, the instances the test setup never resets, its
    posted-body reads, and its errors. It is read beside the test setup, which names the instances it resets."""

    node_type = "NodeRoot"

    def __init__(self, relative: str, text: str, setup_text: str) -> None:
        super().__init__(relative, text)
        self._setup_text = setup_text

    @property
    def facts(self) -> dict:
        text = self._source.text
        store_readers = [
            (name, code)
            for name, body in self._node_repository_bodies()
            if (code := self._store_code(body)) is not None
        ]
        return {
            fact_names.NODE_REPOSITORIES: [
                {"name": name, "raw_io": SourceText(code).hits(_RAW_FILE_IO), "parses_on_read": bool(_SCHEMA_PARSE.search(code))}
                for name, code in store_readers
            ],
            fact_names.UNRESET_INSTANCES: self.unreset_instances([name for name, _code in store_readers], self._setup_text),
            fact_names.UNPARSED_BODY_READS: [
                self._source.line_of(match.start()) for match in _ANY_BODY_READ.finditer(text) if not self._inside_schema_parse(match.start())
            ],
            **self.error_handling_facts(),
        }


class RouteFile(LernFile):
    """An aggregate's `-routes.ts` file: the body reads no schema checks, and its errors."""

    node_type = "Route"

    @property
    def facts(self) -> dict:
        return {fact_names.LOOSE_BODY_READS: self._source.hits(_LOOSE_BODY_READ), **self.error_handling_facts()}


class BehaviorFile(LernFile):
    """A LERN behavior file, shared or for one tier, which becomes the node type its tier names."""

    def __init__(self, relative: str, text: str, node_type: str) -> None:
        super().__init__(relative, text)
        self.node_type = node_type

    @property
    def facts(self) -> dict:
        """What the behavior file says about the tier it reaches and what it stubs."""
        return {
            fact_names.TIER_REACHES: self._source.hits(_TIER_REACH),
            fact_names.RUNS_SHARED_BEHAVIOR: bool(_RUNS_SHARED.search(self._source.text)),
            fact_names.STUBS: self._source.hits(_STUB),
            fact_names.STUBBED_REQUESTS: self._source.hits(_STUBBED_REQUEST),
        }


class StoryTestFile(LernFile):
    """A LERN story test file, shared, server, domain, or playwright, which becomes the node type its tier names."""

    def __init__(self, relative: str, text: str, node_type: str) -> None:
        super().__init__(relative, text)
        self.node_type = node_type

    @property
    def facts(self) -> dict:
        """What the story test file says about its steps and helpers."""
        text = self._source.text
        asserting = []
        for match in _GIVEN_START.finditer(text):
            body = self._callback_body(match.end())
            if body is not None and _EXPECT.search(body):
                asserting.append([self._source.line_of(match.start()), match.group(2)])
        return {
            fact_names.CONTEXT_CASTS: [[self._source.line_of(match.start()), match.group(0)] for match in _CTX_CAST.finditer(text)],
            fact_names.ASSERTING_GIVENS: asserting,
            fact_names.DOMAIN_WRAPPING_HELPERS: self._domain_wrapping_helpers(),
            fact_names.HAND_WRITTEN_ENTRIES: [
                [self._source.line_of(match.start()), match.group("outline"), match.group("entry")]
                for match in _HAND_WRITTEN_ENTRY.finditer(text)
            ],
            fact_names.SCREEN_STORIES: [match.group(2) for match in _DESCRIBED.finditer(text)],
        }

    def _domain_wrapping_helpers(self) -> list[list]:
        """[line, helper, repository calls] for each top-level helper that reaches the repositories."""
        text = self._source.text
        found: list[list] = []
        for match in _TOP_LEVEL_HELPER.finditer(text):
            end = _TOP_LEVEL_END.search(text, match.end())
            calls = sorted(set(_DOMAIN_CALL.findall(text[match.end():end.start() if end else len(text)])))
            if calls:
                found.append([self._source.line_of(match.start()), match.group(1) or match.group(2), calls])
        return found


class AggregateFolder:
    """One aggregate's folder in a LERN working copy, such as `src/subscription`: the facts the LERN rules read about the
    aggregate as a whole come from the files it holds."""

    def __init__(self, root: Path, folder: str) -> None:
        self.root = root
        self.folder = folder

    def core_request_reads(self) -> list[list]:
        """[file, line, code] for each request read in the framework-free core `<folder>/<aggregate>.ts`."""
        core = self.root / self.folder / f"{Path(self.folder).name}.ts"
        return LernFile.at(self.root, core).request_reads() if core.is_file() else []

    def web_path_literals(self) -> list[list]:
        """[file, line, path] for each browser path written as a literal outside the aggregate's `*-paths.ts`."""
        files = sorted((self.root / self.folder).glob("*.ts*"))
        return [found for file in files if not file.name.endswith(_PATHS_MODULE_SUFFIX) for found in LernFile.at(self.root, file).web_path_literals()]
