"""Scanner: detect single-letter variables and generic placeholder names."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

DECL_PATTERN = re.compile(
    r'\b(?:const|let|var)\s+(\w+)'
)
LOOP_ITER = re.compile(
    r'\bfor\s*\(.*\b(?:const|let|var)\s+([ijk])\b'
)
GENERIC_NAMES = {
    'info', 'thing', 'stuff', 'temp', 'data', 'val', 'obj',
    'value', 'item', 'tmp', 'foo', 'bar', 'baz', 'x', 'y',
    'ret', 'res', 'str', 'num', 'arr', 'elem',
}
LOOP_VARS = {'i', 'j', 'k'}


class IntentionRevealingNamesScanner(JsCodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            content = self._read_file(file_path)
            if content is None:
                continue
            for i, line in enumerate(content.split('\n')):
                loop_match = LOOP_ITER.search(line)
                loop_var = loop_match.group(1) if loop_match else None

                for decl in DECL_PATTERN.finditer(line):
                    name = decl.group(1)
                    if name == loop_var:
                        continue
                    is_single = len(name) == 1 and name.isalpha()
                    is_generic = name.lower() in GENERIC_NAMES
                    if is_single and name not in LOOP_VARS:
                        violations.append(self.violation((
                                f"Single-letter variable '{name}' hides intent. "
                                "Use a descriptive name."
                            ), location=str(file_path), line=i + 1))
                    elif is_generic:
                        violations.append(self.violation((
                                f"Generic name '{name}' reveals no intent. "
                                "Name it after what it represents in the domain."
                            ), location=str(file_path), line=i + 1))
        return violations


if __name__ == '__main__':
    from scanners import run_scanner_main
    from js_code_scanner import collect_javascript_files
    raise SystemExit(run_scanner_main(IntentionRevealingNamesScanner, 'use-intention-revealing-names', collect_javascript_files))
