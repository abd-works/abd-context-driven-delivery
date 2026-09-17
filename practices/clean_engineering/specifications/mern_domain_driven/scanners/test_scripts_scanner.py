"""Scanner: verify all required test runner scripts exist and are correct.

Checks:
1. scripts/test.sh and scripts/test.ps1 exist at workspace root.
2. scripts/test-e2e.sh and scripts/test-e2e.ps1 exist.
3. test.sh / test.ps1 invoke 'vitest run' (not playwright).
4. test-e2e.sh / test-e2e.ps1 invoke 'playwright test'.
5. test-e2e scripts include a REQUIRES comment warning about the feature package frontend.
6. playwright.config.ts exists and declares webServer entries for both
   the API server (port 3001) and the React frontend (port 3000).
7. vitest.config.ts exists and excludes *_e2e.spec.ts files.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from mern_scanner_base import TypeScriptScanner
from scan.violation import Violation


class TestScriptsScanner(TypeScriptScanner):
    """Checks test runner scripts exist with correct content."""

    RULE = "scaffold-test-scripts"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        project_root = root

        scripts_dir = project_root / "scripts"

        violations += self._check_script_exists(
            scripts_dir, "test.sh",
            must_contain=["vitest run"],
            must_not_contain=["playwright"],
            hint="Run Vitest unit/component tests.",
        )
        violations += self._check_script_exists(
            scripts_dir, "test.ps1",
            must_contain=["vitest run"],
            must_not_contain=["playwright"],
            hint="Run Vitest unit/component tests (Windows).",
        )
        violations += self._check_script_exists(
            scripts_dir, "test-e2e.sh",
            must_contain=["playwright test"],
            must_not_contain=["vitest"],
            hint="Run Playwright E2E tests.",
            requires_comment=True,
        )
        violations += self._check_script_exists(
            scripts_dir, "test-e2e.ps1",
            must_contain=["playwright test"],
            must_not_contain=["vitest"],
            hint="Run Playwright E2E tests (Windows).",
            requires_comment=True,
        )

        violations += self._check_playwright_config(project_root)
        violations += self._check_vitest_config(project_root)

        return violations

    def _check_script_exists(
        self,
        scripts_dir: Path,
        filename: str,
        must_contain: List[str],
        must_not_contain: List[str],
        hint: str,
        requires_comment: bool = False,
    ) -> List[Violation]:
        violations: List[Violation] = []
        script = scripts_dir / filename

        if not script.exists():
            violations.append(
                self.v(
                    f"Missing scripts/{filename}. {hint} "
                    "Create it at the workspace root so tests are runnable "
                    "without memorising npm script names.",
                    str(scripts_dir),
                )
            )
            return violations

        content = script.read_text(encoding="utf-8", errors="replace")

        for required in must_contain:
            if required not in content:
                violations.append(
                    self.v(f"scripts/{filename} does not contain '{required}'. {hint}", str(script))
                )

        for forbidden in must_not_contain:
            if forbidden in content:
                violations.append(
                    self.v(
                        f"scripts/{filename} contains '{forbidden}' but should not. "
                        "Keep test tiers separate: Vitest for unit/component, "
                        "Playwright for E2E.",
                        str(script),
                    )
                )

        if requires_comment and "REQUIRES" not in content.upper():
            violations.append(
                self.v(
                    f"scripts/{filename} is missing a REQUIRES comment explaining "
                    "that the feature package must serve the React frontend before "
                    "E2E tests can pass. Add: # REQUIRES: packages/<epicSlug> must "
                    "exist and `npm run dev` must serve the React frontend.",
                    str(script),
                    severity="warning",
                )
            )

        return violations

    def _check_playwright_config(self, project_root: Path) -> List[Violation]:
        violations: List[Violation] = []
        config = project_root / "playwright.config.ts"

        if not config.exists():
            violations.append(
                self.v(
                    "playwright.config.ts is missing. Without it, Playwright picks "
                    "up Vitest test files and fails with ESM/CJS errors. "
                    "Create playwright.config.ts with testMatch: '**/*_e2e.spec.ts'.",
                    str(project_root),
                )
            )
            return violations

        content = config.read_text(encoding="utf-8", errors="replace")

        if "webServer" not in content:
            violations.append(
                self.v(
                    "playwright.config.ts has no webServer configuration. "
                    "Add webServer entries for both the API server (port 3001) "
                    "and the React frontend (port 3000) so Playwright starts them.",
                    str(config),
                )
            )
        else:
            if "3001" not in content and "serve.ts" not in content and "app.ts" not in content:
                violations.append(
                    self.v(
                        "playwright.config.ts webServer does not appear to start the "
                        "API server (expected port 3001 or serve.ts/app.ts reference). "
                        "E2E tests need the Express backend running.",
                        str(config),
                        severity="warning",
                    )
                )
            if "3000" not in content and "vite" not in content and "main.tsx" not in content:
                violations.append(
                    self.v(
                        "playwright.config.ts webServer does not appear to start the "
                        "React frontend (expected port 3000 or vite/main.tsx reference). "
                        "E2E tests need the feature package frontend serving page routes.",
                        str(config),
                        severity="warning",
                    )
                )

        if "*_e2e.spec.ts" not in content and "e2e.spec" not in content:
            violations.append(
                self.v(
                    "playwright.config.ts testMatch does not appear to target "
                    "*_e2e.spec.ts files. Set testMatch: '**/*_e2e.spec.ts' to "
                    "prevent picking up Vitest test files.",
                    str(config),
                )
            )

        return violations

    def _check_vitest_config(self, project_root: Path) -> List[Violation]:
        violations: List[Violation] = []
        config = project_root / "vitest.config.ts"

        if not config.exists():
            violations.append(
                self.v(
                    "vitest.config.ts is missing. Without it, Vitest picks up "
                    "*_e2e.spec.ts Playwright files and fails. Create vitest.config.ts "
                    "with include patterns for *_server.test.ts and *_client.test.tsx only.",
                    str(project_root),
                )
            )
            return violations

        content = config.read_text(encoding="utf-8", errors="replace")

        if "_e2e.spec" not in content and "e2e" not in content.lower():
            violations.append(
                self.v(
                    "vitest.config.ts does not appear to exclude E2E spec files. "
                    "Add include: ['tests/**/*_server.test.ts', 'tests/**/*_client.test.tsx'] "
                    "to prevent picking up Playwright test files.",
                    str(config),
                    severity="warning",
                )
            )

        return violations
