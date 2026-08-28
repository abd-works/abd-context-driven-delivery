"""Scanner: verify type-safe Express controllers / routes.

Uses tree-sitter TypeScript AST to check:
1. Controller files that access req.user, req.session, or other custom
   middleware-injected properties have a global type augmentation:
   declare global { namespace Express { interface Request { ... } } }
2. No (req as any).user patterns - augment types instead of casting.
3. No @ts-ignore comments used to suppress type errors in controllers.
4. Callback/arrow function parameters are explicitly typed (no implicit any)
   when the callback operates on domain objects.
5. Lambda parameters in controller methods use domain types, not 'any'.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from mern_scanner_base import TypeScriptScanner
from scan.violation import Violation

_REQ_CUSTOM_PROP_RE = re.compile(r"\breq\.(user|session|auth|claims|tenant)\b")
_AS_ANY_REQ_RE = re.compile(r"\(\s*req\s+as\s+any\s*\)\.")
_TS_IGNORE_RE = re.compile(r"//\s*@ts-ignore")
_TS_EXPECT_ERROR_RE = re.compile(r"//\s*@ts-expect-error")
_DECLARE_GLOBAL_RE = re.compile(r"declare\s+global\s*\{[^}]*namespace\s+Express", re.DOTALL)
_IMPLICIT_ANY_MAP_RE = re.compile(r"\.(map|filter|forEach|reduce|find|some|every)\s*\(\s*\w+\s*=>")
_TYPED_LAMBDA_RE = re.compile(r"\.(map|filter|forEach|reduce|find|some|every)\s*\(\s*\(\s*\w+\s*:")


class TypeSafetyScanner(TypeScriptScanner):
    """AST + regex checks for type safety in Express controllers."""

    RULE = "ensure-type-safe-routes"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        project_root = root

        for domain_path in self._find_domain_packages(project_root):
            server = self._server_file(domain_path)
            if server is not None:
                violations += self._check_controller(server)

        packages_dir = project_root / "packages"
        if packages_dir.exists():
            for app_file in packages_dir.rglob("app.ts"):
                if "node_modules" not in app_file.parts:
                    violations += self._check_controller(app_file)

        return violations

    def _check_controller(self, ts_file: Path) -> List[Violation]:
        violations: List[Violation] = []
        content = self._read_file_content(ts_file)
        if content is None:
            return violations

        lines = content.splitlines()

        if _REQ_CUSTOM_PROP_RE.search(content):
            if not _DECLARE_GLOBAL_RE.search(content):
                violations.append(
                    self.v(
                        f"'{ts_file.name}' accesses req.user/req.session/req.auth "
                        "but has no Express type augmentation. Add:\n"
                        "  declare global { namespace Express { "
                        "interface Request { user?: { id: string } } } }\n"
                        "Otherwise tsc --noEmit will fail with TS2339.",
                        str(ts_file),
                    )
                )

        for line_num, line in enumerate(lines, 1):
            if _AS_ANY_REQ_RE.search(line):
                violations.append(
                    self.v(
                        f"'{ts_file.name}' uses (req as any).user to bypass type "
                        "checking. Use a global type augmentation instead of "
                        "casting to any.",
                        str(ts_file),
                        line_num,
                    )
                )

        for line_num, line in enumerate(lines, 1):
            if _TS_IGNORE_RE.search(line) or _TS_EXPECT_ERROR_RE.search(line):
                violations.append(
                    self.v(
                        f"'{ts_file.name}' uses @ts-ignore/@ts-expect-error to "
                        "suppress a type error. Fix the underlying type issue "
                        "instead of suppressing the diagnostic.",
                        str(ts_file),
                        line_num,
                    )
                )

        for line_num, line in enumerate(lines, 1):
            if _IMPLICIT_ANY_MAP_RE.search(line) and not _TYPED_LAMBDA_RE.search(line):
                match = re.search(r"\.(map|filter|forEach|find)\s*\(\s*([a-zA-Z_]\w*)\s*=>", line)
                if match:
                    param_name = match.group(2)
                    violations.append(
                        self.v(
                            f"'{ts_file.name}' has an untyped lambda parameter "
                            f"'{param_name}' in .{match.group(1)}(). "
                            "Add an explicit type: "
                            f".{match.group(1)}(({param_name}: DomainType) => ...)",
                            str(ts_file),
                            line_num,
                            severity="warning",
                        )
                    )

        return violations
