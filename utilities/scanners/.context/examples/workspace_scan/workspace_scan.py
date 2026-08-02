"""Example: run the full scanner suite across a workspace root and return violations."""

from __future__ import annotations

from pathlib import Path

from scanners.scan import Scan


class WorkspaceScan(Scan):
    """Run the default scanner collection against every file under a root path."""

    def run(self, root_path: str) -> dict:
        """Scan all files under *root_path* and return the violation report as a dict.

        Walks the directory tree, collects every file path, passes the list
        to ``scan``, and converts the result string back to a dict via ``eval``
        so the caller can inspect violations programmatically.
        """
        files = [
            str(p)
            for p in Path(root_path).rglob("*")
            if p.is_file()
        ]
        raw = self.scan(paths=files)
        # scan() returns str(report.to_dict()); convert back to a plain dict.
        import ast
        return ast.literal_eval(raw)
