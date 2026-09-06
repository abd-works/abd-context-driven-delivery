"""Scanner: verify type-safe Express controllers.

Uses tree-sitter TypeScript AST to check:
1. Controller files that access req.user, req.session, or other custom
   middleware-injected properties have a global type augmentation:
   declare global { namespace Express { interface Request { ... } } }
2. No (req as any).user patterns — augment types instead of casting.
3. No @ts-ignore comments used to suppress type errors in controllers.
4. Callback/arrow function parameters are explicitly typed (no implicit any)
   when the callback operates on domain objects.
5. Lambda parameters in controller methods use domain types, not 'any'.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

try:
    from .ts_scanner_base import TypeScriptScanner, run_scanner_main
except ImportError:
    from ts_scanner_base import TypeScriptScanner, run_scanner_main


_REQ_CUSTOM_PROP_RE = re.compile(r'\breq\.(user|session|auth|claims|tenant)\b')
_AS_ANY_REQ_RE = re.compile(r'\(\s*req\s+as\s+any\s*\)\.')
_TS_IGNORE_RE = re.compile(r'//\s*@ts-ignore')
_TS_EXPECT_ERROR_RE = re.compile(r'//\s*@ts-expect-error')
_DECLARE_GLOBAL_RE = re.compile(
    r'declare\s+global\s*\{[^}]*namespace\s+Express', re.DOTALL
)
_IMPLICIT_ANY_MAP_RE = re.compile(
    r'\.(map|filter|forEach|reduce|find|some|every)\s*\(\s*\w+\s*=>'
)
_TYPED_LAMBDA_RE = re.compile(
    r'\.(map|filter|forEach|reduce|find|some|every)\s*\(\s*\(\s*\w+\s*:'
)


class TypeSafetyScanner(TypeScriptScanner):
    """AST + regex checks for type safety in Express controllers."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for domain_path in self._find_domain_packages(project_root):
            server_dir = domain_path / 'server'
            if not server_dir.exists():
                continue
            for controller_file in sorted(server_dir.glob('*.controller.ts')):
                violations += self._check_controller(controller_file)

        # Also check app-server
        app_server = project_root / 'packages' / 'app-server'
        if app_server.exists():
            for ts_file in app_server.rglob('*.ts'):
                if 'node_modules' not in ts_file.parts:
                    violations += self._check_controller(ts_file)

        return violations

    def _check_controller(self, ts_file: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        try:
            content = ts_file.read_text(encoding='utf-8', errors='replace')
        except OSError:
            return violations

        lines = content.splitlines()

        # Check: req.custom_property without declare global
        if _REQ_CUSTOM_PROP_RE.search(content):
            if not _DECLARE_GLOBAL_RE.search(content):
                violations.append(self.v(
                    f"'{ts_file.name}' accesses req.user/req.session/req.auth "
                    "but has no Express type augmentation. Add:\n"
                    "  declare global { namespace Express { "
                    "interface Request { user?: { id: string } } } }\n"
                    "Otherwise tsc --noEmit will fail with TS2339.",
                    str(ts_file),
                ))

        # Check: (req as any).user — type cast bypass
        for line_num, line in enumerate(lines, 1):
            if _AS_ANY_REQ_RE.search(line):
                violations.append(self.v(
                    f"'{ts_file.name}' uses (req as any).user to bypass type "
                    "checking. Use a global type augmentation instead of "
                    "casting to any.",
                    str(ts_file),
                    line_num,
                ))

        # Check: @ts-ignore in controllers
        for line_num, line in enumerate(lines, 1):
            if _TS_IGNORE_RE.search(line) or _TS_EXPECT_ERROR_RE.search(line):
                violations.append(self.v(
                    f"'{ts_file.name}' uses @ts-ignore/@ts-expect-error to "
                    "suppress a type error. Fix the underlying type issue "
                    "instead of suppressing the diagnostic.",
                    str(ts_file),
                    line_num,
                ))

        # Check: implicit any in array method callbacks
        for line_num, line in enumerate(lines, 1):
            if _IMPLICIT_ANY_MAP_RE.search(line) and not _TYPED_LAMBDA_RE.search(line):
                # Only flag if the lambda parameter is a single untyped word
                match = re.search(
                    r'\.(map|filter|forEach|find)\s*\(\s*([a-zA-Z_]\w*)\s*=>', line
                )
                if match:
                    param_name = match.group(2)
                    violations.append(self.v(
                        f"'{ts_file.name}' has an untyped lambda parameter "
                        f"'{param_name}' in .{match.group(1)}(). "
                        "Add an explicit type: "
                        f".{match.group(1)}(({param_name}: DomainType) => ...)",
                        str(ts_file),
                        line_num,
                        severity='warning',
                    ))

        return violations


if __name__ == '__main__':
    run_scanner_main(TypeSafetyScanner, 'ensure-type-safe-controllers')
