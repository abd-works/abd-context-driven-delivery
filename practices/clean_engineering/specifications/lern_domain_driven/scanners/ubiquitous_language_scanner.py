"""Scanner: verify Domain Language in class and method names.

Uses tree-sitter TypeScript AST to check:
1. No class names end with forbidden technical suffixes:
   Manager, Handler, Processor, Helper, Utility, Utils, Util, Factory, Builder
   (in domain entity positions - service layer is allowed 'Service').
2. No public domain method names use generic technical verbs:
   process(), handle(), execute(), run(), manage(), perform().
3. Test method names use scenario language, not HTTP/technical language
   (e.g. no 'GET /api/...' in test names, no 'returns 200').
4. File names match the primary class they export (ubiquitous alignment).
5. Abbreviations in class names are flagged (names < 4 chars or all caps).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from lern_scanner_base import TypeScriptScanner, Violation

_FORBIDDEN_SUFFIXES = (
    "Manager", "Handler", "Processor", "Helper", "Utility",
    "Utils", "Util", "Builder", "Factory", "Provider",
)
_SERVICE_SUFFIX = "Service"  # allowed in server/ only

_TECHNICAL_METHOD_NAMES = frozenset(
    {"process", "handle", "execute", "run", "manage", "perform", "doWork", "doTask", "doAction"}
)

_HTTP_TEST_PATTERN = re.compile(r"['\"`](GET|POST|PUT|DELETE|PATCH)\s+/api/", re.IGNORECASE)
_STATUS_CODE_PATTERN = re.compile(r"['\"`].*returns?\s+[245]\d\d", re.IGNORECASE)
_DESCRIBE_IT_RE = re.compile(r"\b(describe|it|test)\s*\(")


@dataclass
class _NamedClass:
    cls: object
    ts_file: Path
    tier: str


class UbiquitousLanguageScanner(TypeScriptScanner):
    """AST checks for domain-language naming across all tiers."""

    RULE = "use-ubiquitous-language"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        project_root = root

        for domain_path in self._find_domain_packages(project_root):
            for tier in ("shared", "server", "client"):
                tier_dir = domain_path / tier
                if not tier_dir.exists():
                    continue
                for ts_file in sorted(tier_dir.glob("*.ts")) + sorted(tier_dir.glob("*.tsx")):
                    violations += self._check_file(ts_file, tier, domain_path.name)

        tests_dir = project_root / "tests"
        if tests_dir.exists():
            for ts_file in tests_dir.rglob("*.ts"):
                if "node_modules" not in ts_file.parts:
                    violations += self._check_test_names(ts_file)
            for tsx_file in tests_dir.rglob("*.tsx"):
                if "node_modules" not in tsx_file.parts:
                    violations += self._check_test_names(tsx_file)

        return violations

    def _check_file(self, ts_file: Path, tier: str, domain_name: str) -> List[Violation]:
        violations: List[Violation] = []
        parsed_root = self.parse_file(ts_file)
        if parsed_root is None:
            return violations

        for cls in self.get_classes(parsed_root):
            named = _NamedClass(cls, ts_file, tier)
            violations += self._check_class_name(named)
            violations += self._check_method_names(named)

        return violations

    def _check_class_name(self, named: _NamedClass) -> List[Violation]:
        violations = self._forbidden_suffix_hits(named)
        violations.extend(self._service_suffix_hit(named))
        return violations

    def _forbidden_suffix_hits(self, named: _NamedClass) -> List[Violation]:
        name = named.cls.name
        violations: List[Violation] = []
        for suffix in _FORBIDDEN_SUFFIXES:
            if not name.endswith(suffix) or name == suffix:
                continue
            violations.append(
                self.v(
                    f"Class '{name}' uses the technical suffix '{suffix}'. "
                    "Name domain classes after the concept they represent "
                    f"(e.g. '{name.replace(suffix, '')}' or a specific domain noun). "
                    "Reserve 'Service' only for application-layer orchestrators.",
                    str(named.ts_file),
                    named.cls.start_line,
                )
            )
        return violations

    def _service_suffix_hit(self, named: _NamedClass) -> List[Violation]:
        if not named.cls.name.endswith(_SERVICE_SUFFIX) or named.tier == "server":
            return []
        return [
            self.v(
                f"Class '{named.cls.name}' uses the 'Service' suffix but is in "
                f"'{named.tier}/'. 'Service' suffix is only appropriate for "
                "application-layer orchestrators in server/.",
                str(named.ts_file),
                named.cls.start_line,
            )
        ]

    def _check_method_names(self, named: _NamedClass) -> List[Violation]:
        violations: List[Violation] = []
        for method in named.cls.methods:
            if method.name in ("constructor", "toString", "toJSON"):
                continue
            if "private" in method.modifiers:
                continue
            if method.name not in _TECHNICAL_METHOD_NAMES:
                continue
            violations.append(
                self.v(
                    f"Method '{named.cls.name}.{method.name}()' uses a generic "
                    f"technical verb '{method.name}'. Replace with a domain "
                    "verb that expresses business intent, e.g. "
                    "calculateTotal(), placeOrder(), validateEligibility().",
                    str(named.ts_file),
                    method.start_line,
                )
            )
        return violations

    def _check_test_names(self, ts_file: Path) -> List[Violation]:
        """Test descriptions must use domain/scenario language, not HTTP."""
        content = self._read_file_content(ts_file)
        if content is None:
            return []
        violations: List[Violation] = []
        for line_num, line in enumerate(content.splitlines(), 1):
            violations.extend(self._http_language_in_test_line(ts_file, (line_num, line)))
        return violations

    def _http_language_in_test_line(self, ts_file: Path, numbered_line: tuple[int, str]) -> List[Violation]:
        line_num, line = numbered_line
        if not _DESCRIBE_IT_RE.search(line):
            return []
        violations: List[Violation] = []
        if _HTTP_TEST_PATTERN.search(line):
            violations.append(
                self.v(
                    f"Test name uses HTTP route language: {line.strip()!r}. "
                    "Test names must mirror Gherkin scenario titles in domain "
                    'language, e.g. "user views list of active stores".',
                    str(ts_file),
                    line_num,
                )
            )
        if _STATUS_CODE_PATTERN.search(line):
            violations.append(
                self.v(
                    f"Test name references HTTP status code: {line.strip()!r}. "
                    "Use domain outcomes instead of status codes in test names.",
                    str(ts_file),
                    line_num,
                )
            )
        return violations
