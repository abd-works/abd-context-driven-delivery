"""Run every vanilla mamba spec in the repository, one file per subprocess.

Excludes agent BDD specs (`*_agent_spec.py`, which drive a live agent) and the
JavaScript/Playwright specs, plus fixture and illustrated-example trees that are
inputs to other specs rather than suites of their own.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parent.parent
MAMBA = Path(sys.executable).parent / "mamba.exe"
SOURCE_ROOTS = (".",)
EXCLUDED_DIRECTORY_NAMES = {
    ".codeql",
    ".cq",
    ".venv",
    ".git",
    "node_modules",
    "__pycache__",
    ".ruff_cache",
    "sandbox",
    "fixtures",
    "seeds",
    "templates",
}


class SpecSuite:
    def __init__(self, repository: Path) -> None:
        self._repository = repository

    @property
    def spec_files(self) -> list[Path]:
        return sorted(
            path
            for path in self._repository.rglob("*_spec.py")
            if self._is_vanilla_spec(path)
        )

    @property
    def environment(self) -> dict[str, str]:
        environment = dict(os.environ)
        environment["PYTHONPATH"] = os.pathsep.join(
            str((self._repository / root).resolve()) for root in SOURCE_ROOTS
        )
        environment["PYTHONIOENCODING"] = "utf-8"
        return environment

    def _is_vanilla_spec(self, path: Path) -> bool:
        if path.name.endswith("_agent_spec.py"):
            return False
        relative_parts = path.relative_to(self._repository).parts[:-1]
        return not any(
            part in EXCLUDED_DIRECTORY_NAMES or part.startswith(".examples")
            for part in relative_parts
        )

    def run(self) -> int:
        failures: list[dict[str, str]] = []
        spec_files = self.spec_files
        for position, spec in enumerate(spec_files, start=1):
            relative = spec.relative_to(self._repository).as_posix()
            print(f"[{position}/{len(spec_files)}] {relative}", flush=True)
            completed = subprocess.run(
                [str(MAMBA), "--format", "progress", relative],
                cwd=self._repository,
                env=self.environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            output = completed.stdout + completed.stderr
            summary = next(
                (line for line in output.splitlines() if "examples" in line and "ran in" in line),
                "no summary line (spec did not load)",
            )
            print(f"    {summary.strip()}", flush=True)
            if completed.returncode != 0:
                failures.append(
                    {
                        "spec": relative,
                        "exit_code": str(completed.returncode),
                        "summary": summary.strip(),
                        "output": output[-6000:],
                    }
                )
        self._report(spec_files, failures)
        return 1 if failures else 0

    def _report(self, spec_files: list[Path], failures: list[dict[str, str]]) -> None:
        print(f"\n{len(spec_files) - len(failures)}/{len(spec_files)} spec files passed")
        for failure in failures:
            print(f"\nFAILED {failure['spec']} (exit {failure['exit_code']})")
            print(failure["output"])
        results = self._repository / "sandbox" / "mamba_suite_results.json"
        results.write_text(
            json.dumps(
                {"total": len(spec_files), "failures": failures}, indent=2
            ),
            encoding="utf-8",
        )
        print(f"\nDetails written to {results}")


if __name__ == "__main__":
    raise SystemExit(SpecSuite(REPOSITORY).run())
