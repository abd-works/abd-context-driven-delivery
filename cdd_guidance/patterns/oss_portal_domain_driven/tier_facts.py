"""OSS Portal tier facts — read once from each tier file, proxy, and migration while the overlay records its nodes.

The overlay sets these on the ClientRoot, View, BffRoot, BffRoute, ServiceRoot, ServiceRoute, Proxy, Migration, and
Aggregate nodes; the OSS rules read them with ``get_fact`` and never open a file. Story files are read with the LERN
pattern's *TierFile*, because the OSS pattern keeps LERN's shared-story layout.
"""

from __future__ import annotations

import re
from pathlib import Path

from cdd_guidance.practices.clean_engineering.model.operation_metrics import SourceText

# A gateway or service address in browser code: an Apigee base path (`/v1/...`), a Cloud Run URL, or an Apigee host.
_GATEWAY_ADDRESS = re.compile(r"""(['"`])(?:https?://[^'"`]*)?/v\d+/[^'"`]*\1|\.run\.app\b|\bapigee\b""", re.IGNORECASE)
# Token handling the browser must never do: a bearer header, a token field, or a token kept in browser storage.
_TOKEN_HANDLING = re.compile(
    r"""\bBearer\s|['"]Authorization['"]|\bAuthorization\s*:|\b(?:access_?token|id_?token|refresh_?token)\b|\b(?:localStorage|sessionStorage)\.(?:setItem|getItem)\(""",
    re.IGNORECASE,
)
# A view that fetches on its own instead of rendering the client it holds.
_VIEW_FETCH = re.compile(r"\bfetch\(|\bHttpClient\b|\bXMLHttpRequest\b|\baxios\b")
# SQL written in a file: a statement keyword followed by the words that make it a statement.
_SQL = re.compile(r"""\b(?:SELECT\s+[\w*,\s.]+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|CREATE\s+TABLE|ALTER\s+TABLE|DROP\s+TABLE)\b""", re.IGNORECASE)
_SQL_REPOSITORY_CLASS = re.compile(r"\bclass\s+(\w+RepositorySql)\b[^{]*\{")
_IMPORT_FROM = re.compile(r"""^\s*import\b[^;]*?\bfrom\s+['"]([^'"]+)['"]""", re.MULTILINE)
_PUBLISH = re.compile(r"""\.publish(?:Message|JSON)?\(|\btopic\(\s*['"`]""")
_STACK_IN_REPLY = re.compile(r"\bres\.(?:status\(\s*\d+\s*\)\s*\.\s*)?(?:json|send)\s*\([^)]*\b(?:stack|sqlMessage|sql)\b")
_RAW_ERROR_REPLY = re.compile(r"\bres\.(?:status\(\s*\d+\s*\)\s*\.\s*)?(?:json|send)\s*\(\s*(?:err|error|e)\s*\)")
_HARDCODED_SECRET = re.compile(
    r"""\b(?:password|passwd|secret|api_?key|client_?secret|private_?key)\s*[:=]\s*(['"`])[^'"`\s]{4,}\1|-----BEGIN (?:RSA )?PRIVATE KEY-----""",
    re.IGNORECASE,
)
_LOG_CALL = re.compile(r"\b(?:console|logger|log)\.(?:log|info|warn|error|debug)\s*\(([^)]*)\)")
_PERSONAL_FIELD = re.compile(r"\b(?:email|phone|mobile|firstName|lastName|fullName|dateOfBirth|dob|address|password|token)\b", re.IGNORECASE)
_WEB_PATH = re.compile(r"""(['"`])(/(?!v\d+/|bff/|api/)[a-z][a-z0-9-]*(?:/[a-z0-9-]*)*)\1""")
_ROUTE_REGISTRATION = re.compile(r"\b(?:routes?|router|app)\.(?:get|post|put|patch|delete|use|all)(?:<[^>]*>)?\(\s*$")
_ROUTE_CALL_REACH = 40
_PATHS_MODULE_SUFFIX = "-paths.ts"

# What the framework-free core may not import: a UI framework, a web server, a database driver, or a Google Cloud client.
_FRAMEWORK_IMPORT = re.compile(r"^(?:@angular/|express$|pg$|mysql2?$|@google-cloud/|knex$|typeorm$|sequelize$|prisma$|@prisma/)")

# The tier each file suffix is, and the suffixes each tier may not import (§3.2, maintain-layer-purity).
_BROWSER_FORBIDDEN = ("-bff", "-bff-routes", "-service", "-service-routes")
_BFF_FORBIDDEN = ("-service", "-service-routes")

# Apigee policies the standard chain needs (§3.3), by the XML element each policy file declares, in chain order.
POLICY_CHAIN = (
    ("jwt-validation", ("VerifyJWT", "OAuthV2")),
    ("spike-arrest", ("SpikeArrest",)),
    ("json-threat-protection", ("JSONThreatProtection",)),
    ("error-sanitisation", ("RaiseFault", "DefaultFaultRule", "FaultRule")),
    ("audit-logging", ("MessageLogging",)),
)
_POLICY_ROOT = re.compile(r"<(\w+)[\s>]")
_POLICY_NAME = re.compile(r"""<\w+[^>]*\bname=['"]([^'"]+)['"]""")
_STEP_NAME = re.compile(r"<Step>\s*<Name>([^<]+)</Name>", re.DOTALL)
_BASE_PATH = re.compile(r"<BasePath>([^<]*)</BasePath>")
_SSL_INFO = re.compile(r"<SSLInfo>.*?<Enabled>\s*true\s*</Enabled>", re.DOTALL | re.IGNORECASE)

# An expand step only adds; these statements remove or change what the running release still reads (APP-14).
_MIGRATION_STEPS = ("expand", "backfill", "contract")
_DESTRUCTIVE = re.compile(
    r"\bDROP\s+(?:TABLE|COLUMN|INDEX|CONSTRAINT)\b|\bRENAME\s+(?:COLUMN|TO)\b|\bALTER\s+COLUMN\s+\w+\s+(?:TYPE|SET\s+NOT\s+NULL)\b|\bTRUNCATE\b",
    re.IGNORECASE,
)


class OssFile:
    """One OSS Portal tier file read once, with the SourceText that gives each match the line it starts on. The facts
    the OSS rules read about the file are its operations, so its text is wrapped once however many are read."""

    def __init__(self, text: str, relative: str = "") -> None:
        self.text = text
        self.relative = relative
        self._source = SourceText(text)

    @classmethod
    def at(cls, root: Path, path: Path) -> OssFile:
        return cls(path.read_text(encoding="utf-8"), path.relative_to(root).as_posix())

    # Browser tier --------------------------------------------------------------------------------------------------

    def browser_facts(self) -> dict:
        """What a client or view file says about the addresses it calls, the tokens it touches, and what it imports."""
        return {
            "gateway_calls": self._hits_outside_comments(_GATEWAY_ADDRESS),
            "token_handling": self._hits_outside_comments(_TOKEN_HANDLING),
            "layer_crossings": self._imports_ending(_BROWSER_FORBIDDEN),
            "event_publishes": self._source.hits(_PUBLISH),
            "hardcoded_secrets": self._source.hits(_HARDCODED_SECRET),
        }

    def view_facts(self) -> dict:
        return {**self.browser_facts(), "view_fetches": self._hits_outside_comments(_VIEW_FETCH)}

    # Backend-for-Frontend tier ---------------------------------------------------------------------------------------

    def bff_facts(self) -> dict:
        """What a BFF or BFF route file says about what it imports, the SQL it writes, and what it publishes."""
        return {
            "layer_crossings": self._imports_ending(_BFF_FORBIDDEN),
            "sql_outside_repository": self._source.hits(_SQL),
            "event_publishes": self._source.hits(_PUBLISH),
            "hardcoded_secrets": self._source.hits(_HARDCODED_SECRET),
            "personal_data_logged": self._personal_data_logged(),
        }

    # Service tier ----------------------------------------------------------------------------------------------------

    def service_facts(self, service: str) -> dict:
        """What a service file says about SQL outside its repository, imports of another service, and its errors."""
        return {
            "sql_outside_repository": self._sql_outside_repository(),
            "other_service_imports": self._other_service_imports(service),
            "unsanitised_errors": self._source.hits(_STACK_IN_REPLY) + self._source.hits(_RAW_ERROR_REPLY),
            "hardcoded_secrets": self._source.hits(_HARDCODED_SECRET),
            "personal_data_logged": self._personal_data_logged(),
        }

    def service_route_facts(self, service: str) -> dict:
        return {**self.service_facts(service), "sql_outside_repository": self._source.hits(_SQL)}

    # Domain core -----------------------------------------------------------------------------------------------------

    def core_facts(self) -> dict:
        """[line, module] for each framework the framework-free core imports."""
        return {
            "framework_imports": [
                [self._source.line_of(match.start()), match.group(1)] for match in _IMPORT_FROM.finditer(self.text) if _FRAMEWORK_IMPORT.match(match.group(1))
            ]
        }

    def web_path_literals(self) -> list[list]:
        """[file, line, path] for each browser path this file writes as a literal, outside imports, comments, and the
        paths a route registers."""
        found: list[list] = []
        for match in _WEB_PATH.finditer(self.text):
            before = self.text[max(0, match.start() - _ROUTE_CALL_REACH):match.start()]
            if self._in_import(match.start()) or self._in_comment(match.start()) or _ROUTE_REGISTRATION.search(before):
                continue
            found.append([self.relative, self._source.line_of(match.start()), match.group(2)])
        return found

    # Helpers ---------------------------------------------------------------------------------------------------------

    def _imports_ending(self, suffixes: tuple[str, ...]) -> list[list]:
        """[line, module] for each import whose module name ends in one of suffixes."""
        return [
            [self._source.line_of(match.start()), match.group(1)]
            for match in _IMPORT_FROM.finditer(self.text)
            if match.group(1).removesuffix(".js").removesuffix(".ts").endswith(suffixes)
        ]

    def _other_service_imports(self, service: str) -> list[list]:
        """[line, module] for each import that reaches into a different `*-service` folder under src."""
        found: list[list] = []
        for match in _IMPORT_FROM.finditer(self.text):
            module = match.group(1)
            folders = [part for part in module.split("/") if part.endswith("-service")]
            if any(folder != service for folder in folders):
                found.append([self._source.line_of(match.start()), module])
        return found

    def _sql_outside_repository(self) -> list[list]:
        """[line, sql] for SQL written outside every `*RepositorySql` class in the file."""
        inside: list[tuple[int, int]] = []
        for match in _SQL_REPOSITORY_CLASS.finditer(self.text):
            end = self._brace_end(match.end() - 1)
            if end is not None:
                inside.append((match.start(), end))
        return [
            [self._source.line_of(match.start()), match.group(0)]
            for match in _SQL.finditer(self.text)
            if not any(start <= match.start() <= end for start, end in inside)
        ]

    def _personal_data_logged(self) -> list[list]:
        return [
            [self._source.line_of(match.start()), match.group(0)]
            for match in _LOG_CALL.finditer(self.text)
            if _PERSONAL_FIELD.search(match.group(1))
        ]

    def _hits_outside_comments(self, pattern: re.Pattern) -> list[list]:
        return [
            [self._source.line_of(match.start()), match.group(0)]
            for match in pattern.finditer(self.text)
            if not self._in_comment(match.start()) and not self._in_import(match.start())
        ]

    def _brace_end(self, open_brace: int) -> int | None:
        depth = 0
        for index in range(open_brace, len(self.text)):
            if self.text[index] == "{":
                depth += 1
            elif self.text[index] == "}":
                depth -= 1
                if depth == 0:
                    return index
        return None

    def _in_import(self, index: int) -> bool:
        line_start = self.text.rfind("\n", 0, index) + 1
        line_end = self.text.find("\n", index)
        line = self.text[line_start:line_end if line_end != -1 else len(self.text)]
        return line.lstrip().startswith(("import ", "export ")) and " from " in line

    def _in_comment(self, index: int) -> bool:
        line_start = self.text.rfind("\n", 0, index) + 1
        if re.search(r"(?:^|\s)//", self.text[line_start:index]):
            return True
        opened = self.text.rfind("/*", 0, index)
        return opened != -1 and self.text.find("*/", opened, index) == -1


class ProxyFolder:
    """One service's Apigee proxy folder, `src/<service>/<service>-proxy/`: the facts the gateway rules read about the
    whole proxy come from every XML file it holds."""

    def __init__(self, root: Path, folder: Path) -> None:
        self.root = root
        self.folder = folder

    def facts(self) -> dict:
        files = sorted(self.folder.rglob("*.xml"))
        texts = {file.relative_to(self.root).as_posix(): file.read_text(encoding="utf-8") for file in files}
        declared = self._declared_policies(texts)
        steps = [name for text in texts.values() for name in _STEP_NAME.findall(text)]
        return {
            "base_paths": [path.strip() for text in texts.values() for path in _BASE_PATH.findall(text)],
            "missing_policies": [policy for policy, elements in POLICY_CHAIN if not any(element in declared.values() for element in elements)],
            "policy_order": self._order(declared, steps),
            "tls_enabled": any(_SSL_INFO.search(text) for text in texts.values()),
        }

    def _declared_policies(self, texts: dict[str, str]) -> dict[str, str]:
        """Policy name → its root XML element, for each policy file, plus the fault rules an endpoint declares."""
        declared: dict[str, str] = {}
        for text in texts.values():
            root = _POLICY_ROOT.search(text.split("?>", 1)[-1])
            name = _POLICY_NAME.search(text)
            if root and name:
                declared[name.group(1)] = root.group(1)
            for fault in ("DefaultFaultRule", "FaultRule"):
                if f"<{fault}" in text:
                    declared[f"__{fault}"] = fault
        return declared

    def _order(self, declared: dict[str, str], steps: list[str]) -> list[str]:
        """The chain policies in the order the flow steps run them, by chain name."""
        chain_of = {element: policy for policy, elements in POLICY_CHAIN for element in elements}
        ordered: list[str] = []
        for step in steps:
            policy = chain_of.get(declared.get(step.strip(), ""))
            if policy is not None and policy not in ordered:
                ordered.append(policy)
        return ordered


class MigrationFile:
    """One migration in `src/<service>/migrations/`: which expand-and-contract step its name declares, and any
    statement an expand step may not hold."""

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text
        self._source = SourceText(text)

    def facts(self) -> dict:
        step = next((step for step in _MIGRATION_STEPS if re.search(rf"(?:^|[-_.]){step}(?:[-_.]|$)", self.name.lower())), "")
        return {
            "migration_step": step,
            "destructive_statements": self._source.hits(_DESTRUCTIVE) if step == "expand" else [],
        }


class AggregateFolder:
    """One aggregate's folder, `src/<service>/<aggregate>`: the facts about the aggregate as a whole."""

    def __init__(self, root: Path, folder: str) -> None:
        self.root = root
        self.folder = folder

    def web_path_literals(self) -> list[list]:
        """[file, line, path] for each browser path written as a literal outside the aggregate's `*-paths.ts`."""
        files = sorted((self.root / self.folder).glob("*.ts"))
        return [
            found
            for file in files
            if not file.name.endswith(_PATHS_MODULE_SUFFIX) and not file.name.endswith(("-service.ts", "-service-routes.ts"))
            for found in OssFile.at(self.root, file).web_path_literals()
        ]
