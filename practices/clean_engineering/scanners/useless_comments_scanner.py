"""Scanner: detect comments that repeat code instead of explaining why."""
from pathlib import Path

from code_scanner import CodeScanner


class UselessCommentsScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            parsed = self._parse_file(file_path)
            if parsed is None:
                continue
            seen_comment_lines: set[int] = set()
            for module in parsed.model.modules:
                for oclass in module.classes:
                    for line in oclass.narration_comment_lines:
                        if line in seen_comment_lines:
                            continue
                        seen_comment_lines.add(line)
                        text = (
                            parsed.lines[line - 1].strip()
                            if 0 < line <= len(parsed.lines)
                            else ""
                        )
                        violations.append(
                            self.violation(
                                f"Comment narrates code instead of explaining why: '{text[:60]}'",
                                location=str(file_path),
                                line=line,
                            )
                        )
                    for line in oclass.commented_code_lines:
                        if line in seen_comment_lines:
                            continue
                        seen_comment_lines.add(line)
                        violations.append(
                            self.violation(
                                "Commented-out code detected. Remove or use version control.",
                                location=str(file_path),
                                line=line,
                            )
                        )
                    if oclass.name != "_module" and oclass.docstring_parrots_name:
                        violations.append(
                            self.violation(
                                f"Docstring for '{oclass.name}' just repeats its name.",
                                location=str(file_path),
                                line=oclass.line,
                            )
                        )
                    for op in oclass.operations:
                        if op.docstring_parrots_name:
                            violations.append(
                                self.violation(
                                    f"Docstring for '{op.name}' just repeats its name.",
                                    location=str(file_path),
                                    line=op.line,
                                )
                            )
        return violations


if __name__ == "__main__":
    from scan import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(
            UselessCommentsScanner, "stop-writing-useless-comments", collect_python_files
        )
    )
