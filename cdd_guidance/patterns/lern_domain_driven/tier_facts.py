"""LERN tier facts — read once from tier files while the overlay records its nodes.

The recorder sets these on the NodeRoot, Route, Aggregate, Repository, and StoryShared nodes;
the LERN rules read them with ``get_fact`` and never open a file.
"""

from __future__ import annotations

import re
from pathlib import Path

from cdd_guidance.practices.clean_engineering.model.operation_metrics import SourceText

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
_TEST_SETUP_GLOBS = ("tests/**/vitest.setup.ts", "tests/**/repositories.ts", "tests/vitest.setup.ts")



class TierFile:
    """One LERN file read once — a tier file, a behavior file, or a story file — with the SourceText that gives each
    match in it the line it starts on. The facts the LERN rules read about the file are its operations, so its text is
    wrapped once however many facts are read from it."""

    def __init__(self, text: str, relative: str = "") -> None:
        self.text = text
        # The file's path from the working copy's root, which a fact naming a file records.
        self.relative = relative
        self._source = SourceText(text)

    @classmethod
    def at(cls, root: Path, path: Path) -> TierFile:
        """The file at path, read now, named from root."""
        return cls(path.read_text(encoding="utf-8"), path.relative_to(root).as_posix())

    def node_root_facts(self, setup_text: str) -> dict:
        """What a `-node.ts` file says about its store-reading repositories, posted-body reads, and errors."""
        text = self.text
        store_readers = [
            (name, code)
            for name, body in self._node_repository_bodies()
            if (code := self._store_code(body)) is not None
        ]
        return {
            "node_repositories": [
                {"name": name, "raw_io": SourceText(code).hits(_RAW_FILE_IO), "parses_on_read": bool(_SCHEMA_PARSE.search(code))}
                for name, code in store_readers
            ],
            "unreset_instances": self.unreset_instances([name for name, _code in store_readers], setup_text),
            "unparsed_body_reads": [
                self._source.line_of(match.start()) for match in _ANY_BODY_READ.finditer(text) if not self._inside_schema_parse(match.start())
            ],
            **self.error_handling_facts(),
        }

    def route_facts(self) -> dict:
        return {"loose_body_reads": self._source.hits(_LOOSE_BODY_READ), **self.error_handling_facts()}

    def error_handling_facts(self) -> dict:
        return {"ad_hoc_throws": self._source.hits(_AD_HOC_THROW), "error_replies": self._source.hits(_ERROR_STATUS_REPLY)}

    def request_reads(self) -> list[list]:
        """[file, line, code] for each request read in this file."""
        return [[self.relative, self._source.line_of(match.start()), match.group(0)] for match in _ANY_REQUEST_READ.finditer(self.text)]

    def web_path_literals(self) -> list[list]:
        """[file, line, path] for each browser path this file writes as a literal: not in an import or a comment, and
        not an API path a route registers."""
        text = self.text
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

    def behavior_facts(self) -> dict:
        """What a LERN behavior file (shared or one tier) says about the tier it reaches and what it stubs."""
        return {
            "tier_reaches": self._source.hits(_TIER_REACH),
            "runs_shared_behavior": bool(_RUNS_SHARED.search(self.text)),
            "stubs": self._source.hits(_STUB),
            "stubbed_requests": self._source.hits(_STUBBED_REQUEST),
        }

    def story_facts(self) -> dict:
        """What a LERN story file (shared, server, domain, or playwright) says about its steps and helpers."""
        text = self.text
        asserting = []
        for match in _GIVEN_START.finditer(text):
            body = self._callback_body(match.end())
            if body is not None and _EXPECT.search(body):
                asserting.append([self._source.line_of(match.start()), match.group(2)])
        return {
            "context_casts": [[self._source.line_of(match.start()), match.group(0)] for match in _CTX_CAST.finditer(text)],
            "asserting_givens": asserting,
            "domain_wrapping_helpers": self._domain_wrapping_helpers(),
            "hand_written_entries": [
                [self._source.line_of(match.start()), match.group("outline"), match.group("entry")]
                for match in _HAND_WRITTEN_ENTRY.finditer(text)
            ],
        }

    def _domain_wrapping_helpers(self) -> list[list]:
        """[line, helper, repository calls] for each top-level helper that reaches the repositories."""
        text = self.text
        found: list[list] = []
        for match in _TOP_LEVEL_HELPER.finditer(text):
            end = _TOP_LEVEL_END.search(text, match.end())
            calls = sorted(set(_DOMAIN_CALL.findall(text[match.end():end.start() if end else len(text)])))
            if calls:
                found.append([self._source.line_of(match.start()), match.group(1) or match.group(2), calls])
        return found

    def _store_code(self, class_body: str) -> str | None:
        """The code a node repository reads its store with: its body plus the same-file functions it calls.

        None when the class never touches a store, as with a wrapper that delegates to another repository.
        """
        text = self.text
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
        text = self.text
        statement_start = max(text.rfind(";", 0, index), text.rfind("{\n", 0, index), text.rfind("=>", 0, index))
        before = text[statement_start + 1:index]
        call = _SCHEMA_PARSE.search(before)
        if call is None:
            return False
        opened = before[call.end():]
        return opened.count("(") + 1 > opened.count(")")

    def _node_repository_bodies(self) -> list[tuple[str, str]]:
        """Each `class …RepositoryNode { … }` in the file, with its body."""
        text = self.text
        found: list[tuple[str, str]] = []
        for match in _NODE_REPOSITORY_CLASS.finditer(text):
            body = self._braced_body(match.end() - 1)
            if body is not None:
                found.append((match.group(1), body))
        return found

    def _callback_body(self, start: int) -> str | None:
        """The `{ … }` body of the arrow function that starts at or after ``start``."""
        text = self.text
        open_brace = text.find("{", start)
        arrow = text.find("=>", start)
        if open_brace == -1 or arrow == -1 or arrow > open_brace:
            return None
        return self._braced_body(open_brace)

    def _braced_body(self, open_brace: int) -> str | None:
        text = self.text
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

    def _in_import(self, index: int) -> bool:
        text = self.text
        line_start = text.rfind("\n", 0, index) + 1
        line_end = text.find("\n", index)
        line = text[line_start:line_end if line_end != -1 else len(text)]
        return line.lstrip().startswith(("import ", "export ")) and " from " in line

    def _in_comment(self, index: int) -> bool:
        """A path a doc or line comment names is prose, not a literal the code uses."""
        text = self.text
        line_start = text.rfind("\n", 0, index) + 1
        if re.search(r"(?:^|\s)//", text[line_start:index]):
            return True
        opened = text.rfind("/*", 0, index)
        return opened != -1 and text.find("*/", opened, index) == -1

    def _exported_instance(self, class_name: str) -> str | None:
        text = self.text
        for match in _EXPORTED_INSTANCE.finditer(text):
            if match.group(2) == class_name:
                return match.group(1)
        return None


class AggregateFolder:
    """One aggregate's folder in a LERN working copy, such as `src/subscription`: the facts the LERN rules read about the
    aggregate as a whole come from the files it holds."""

    def __init__(self, root: Path, folder: str) -> None:
        self.root = root
        self.folder = folder

    def core_request_reads(self) -> list[list]:
        """[file, line, code] for each request read in the framework-free core `<folder>/<aggregate>.ts`."""
        core = self.root / self.folder / f"{Path(self.folder).name}.ts"
        return TierFile.at(self.root, core).request_reads() if core.is_file() else []

    def web_path_literals(self) -> list[list]:
        """[file, line, path] for each browser path written as a literal outside the aggregate's `*-paths.ts`."""
        files = sorted((self.root / self.folder).glob("*.ts*"))
        return [found for file in files if not file.name.endswith(_PATHS_MODULE_SUFFIX) for found in TierFile.at(self.root, file).web_path_literals()]


def test_setup_text(root: Path, story_test_folder: str) -> str:
    """The text of every test setup file under root, which a reset repository instance is named in, including the
    repositories file in the pattern's story_test_folder."""
    seen: set[Path] = set()
    parts: list[str] = []
    for pattern in (*_TEST_SETUP_GLOBS, f"{story_test_folder}/repositories.ts"):
        for path in root.glob(pattern):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)
