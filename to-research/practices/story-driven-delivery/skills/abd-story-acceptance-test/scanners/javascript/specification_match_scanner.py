"""Scanner for detecting test names that don't use specification/behavioral language."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

_TEST_NAME = re.compile(
    r'''^\s*(?:it|test)\s*\(\s*['"`]([^'"`]+)['"`]'''
)

_DESCRIBE_NAME = re.compile(
    r'''^\s*describe\s*\(\s*['"`]([^'"`]+)['"`]'''
)

_GENERIC_TEST_NAMES = re.compile(
    r'^(?:test\s*\d+|it\s+works|works\s+correctly|basic\s+test|should\s+work|'
    r'happy\s+path|default\s+case|simple\s+test|test\s+case|todo|fixme|'
    r'does\s+something|handles\s+it|check\s+it|runs?\s+ok)$',
    re.IGNORECASE
)

_BEHAVIORAL_MARKERS = re.compile(
    r'\b(?:should|when|given|then|returns?|creates?|rejects?|throws?|'
    r'accepts?|validates?|calculates?|formats?|filters?|sends?|'
    r'displays?|renders?|emits?|notifies?|updates?|removes?|adds?|'
    r'if|for|with|without|after|before)\b',
    re.IGNORECASE
)

_DOMAIN_WORD = re.compile(r'[a-zA-Z]{4,}')


class SpecificationMatchScanner(JSCodeScanner):
    """Detects test names that don't match specification/behavioral language."""

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in _JS_EXTS):
            return violations
        if not self._is_test_file(path_str):
            return violations
        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            tm = _TEST_NAME.match(line)
            if tm:
                name = tm.group(1).strip()
                v = self._check_test_name(name, file_path, line_num)
                if v:
                    violations.append(v)
                continue

            dm = _DESCRIBE_NAME.match(line)
            if dm:
                name = dm.group(1).strip()
                v = self._check_describe_name(name, file_path, line_num)
                if v:
                    violations.append(v)

        return violations

    def _check_test_name(self, name, file_path, line_num):
        if _GENERIC_TEST_NAMES.match(name):
            return Violation(
                rule=self.rule,
                violation_message=(
                    f'Test name "{name}" is generic. '
                    'Use behavioral language that describes the specification (e.g. "should reject expired tokens").'
                ),
                location=str(file_path),
                line_number=line_num,
                severity='warning'
            ).to_dict()

        if not _BEHAVIORAL_MARKERS.search(name):
            domain_words = _DOMAIN_WORD.findall(name)
            if len(domain_words) < 2:
                return Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test name "{name}" lacks behavioral language. '
                        'Include specification verbs (should, when, returns, validates, etc.) '
                        'and domain terms.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='info'
                ).to_dict()
        return None

    def _check_describe_name(self, name, file_path, line_num):
        if len(name) < 3:
            return Violation(
                rule=self.rule,
                violation_message=(
                    f'describe name "{name}" is too short. '
                    'Use a meaningful domain term or feature name.'
                ),
                location=str(file_path),
                line_number=line_num,
                severity='info'
            ).to_dict()
        return None

    def _is_test_file(self, path_str: str) -> bool:
        return any(marker in path_str for marker in (
            '.test.', '.spec.', '__tests__', '/test/', '\\test\\'
        ))
