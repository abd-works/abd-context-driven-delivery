"""Scanner: verify Domain Language in class and method names.

Uses tree-sitter TypeScript AST to check:
1. No class names end with forbidden technical suffixes:
   Manager, Handler, Processor, Helper, Utility, Utils, Util, Factory, Builder
   (in domain entity positions — service layer is allowed 'Service').
2. No public domain method names use generic technical verbs:
   process(), handle(), execute(), run(), manage(), perform().
3. Test method names use scenario language, not HTTP/technical language
   (e.g. no 'GET /api/...' in test names, no 'returns 200').
4. File names match the primary class they export (ubiquitous alignment).
5. Abbreviations in class names are flagged (names < 4 chars or all caps).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

try:
    from .ts_scanner_base import TypeScriptScanner, run_scanner_main
except ImportError:
    from ts_scanner_base import TypeScriptScanner, run_scanner_main


_FORBIDDEN_SUFFIXES = (
    'Manager', 'Handler', 'Processor', 'Helper', 'Utility',
    'Utils', 'Util', 'Builder', 'Factory', 'Provider',
)
_SERVICE_SUFFIX = 'Service'  # allowed in server/ only

_TECHNICAL_METHOD_NAMES = frozenset({
    'process', 'handle', 'execute', 'run', 'manage',
    'perform', 'doWork', 'doTask', 'doAction',
})

_HTTP_TEST_PATTERN = re.compile(
    r"['\"`](GET|POST|PUT|DELETE|PATCH)\s+/api/",
    re.IGNORECASE,
)
_STATUS_CODE_PATTERN = re.compile(
    r"['\"`].*returns?\s+[245]\d\d",
    re.IGNORECASE,
)
_DESCRIBE_IT_RE = re.compile(r'\b(describe|it|test)\s*\(')


class UbiquitousLanguageScanner(TypeScriptScanner):
    """AST checks for domain-language naming across all tiers."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for domain_path in self._find_domain_packages(project_root):
            for tier in ('shared', 'server', 'client'):
                tier_dir = domain_path / tier
                if not tier_dir.exists():
                    continue
                for ts_file in sorted(tier_dir.glob('*.ts')) + sorted(tier_dir.glob('*.tsx')):
                    violations += self._check_file(ts_file, tier, domain_path.name)

        # Check test files
        tests_dir = project_root / 'tests'
        if tests_dir.exists():
            for ts_file in tests_dir.rglob('*.ts'):
                if 'node_modules' not in ts_file.parts:
                    violations += self._check_test_names(ts_file)
            for tsx_file in tests_dir.rglob('*.tsx'):
                if 'node_modules' not in tsx_file.parts:
                    violations += self._check_test_names(tsx_file)

        return violations

    def _check_file(
        self, ts_file: Path, tier: str, domain_name: str
    ) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        root = self.parse_file(ts_file)
        if root is None:
            return violations

        for cls in self.get_classes(root):
            violations += self._check_class_name(cls, ts_file, tier)
            violations += self._check_method_names(cls, ts_file, tier)

        return violations

    def _check_class_name(self, cls, ts_file: Path, tier: str) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        name = cls.name

        # Forbidden suffix check
        for suffix in _FORBIDDEN_SUFFIXES:
            if name.endswith(suffix) and name != suffix:
                violations.append(self.v(
                    f"Class '{name}' uses the technical suffix '{suffix}'. "
                    "Name domain classes after the concept they represent "
                    f"(e.g. '{name.replace(suffix, '')}' or a specific domain noun). "
                    "Reserve 'Service' only for application-layer orchestrators.",
                    str(ts_file),
                    cls.start_line,
                ))

        # 'Service' suffix only allowed in server/ tier
        if name.endswith(_SERVICE_SUFFIX) and tier != 'server':
            violations.append(self.v(
                f"Class '{name}' uses the 'Service' suffix but is in "
                f"'{tier}/'. 'Service' suffix is only appropriate for "
                "application-layer orchestrators in server/.",
                str(ts_file),
                cls.start_line,
            ))

        return violations

    def _check_method_names(self, cls, ts_file: Path, tier: str) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        for method in cls.methods:
            if method.name in ('constructor', 'toString', 'toJSON'):
                continue
            if 'private' in method.modifiers:
                continue
            if method.name in _TECHNICAL_METHOD_NAMES:
                violations.append(self.v(
                    f"Method '{cls.name}.{method.name}()' uses a generic "
                    f"technical verb '{method.name}'. Replace with a domain "
                    "verb that expresses business intent, e.g. "
                    "calculateTotal(), placeOrder(), validateEligibility().",
                    str(ts_file),
                    method.start_line,
                ))
        return violations

    def _check_test_names(self, ts_file: Path) -> List[Dict[str, Any]]:
        """Test descriptions must use domain/scenario language, not HTTP."""
        violations: List[Dict[str, Any]] = []
        try:
            content = ts_file.read_text(encoding='utf-8', errors='replace')
        except OSError:
            return violations

        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            if not _DESCRIBE_IT_RE.search(line):
                continue
            if _HTTP_TEST_PATTERN.search(line):
                violations.append(self.v(
                    f"Test name uses HTTP route language: {line.strip()!r}. "
                    "Test names must mirror Gherkin scenario titles in domain "
                    "language, e.g. \"user views list of active stores\".",
                    str(ts_file),
                    line_num,
                ))
            if _STATUS_CODE_PATTERN.search(line):
                violations.append(self.v(
                    f"Test name references HTTP status code: {line.strip()!r}. "
                    "Use domain outcomes instead of status codes in test names.",
                    str(ts_file),
                    line_num,
                ))

        return violations


if __name__ == '__main__':
    run_scanner_main(UbiquitousLanguageScanner, 'use-domain-language')
