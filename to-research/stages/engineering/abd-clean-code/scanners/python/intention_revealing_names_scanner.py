"""Scanner: detect names that hide intention — single-letter, generic, or ultra-short."""
import ast
from pathlib import Path
from code_scanner import CodeScanner

LOOP_VARS = {'i', 'j', 'k', 'n', 'x', 'y', 'z', '_', '__'}
GENERIC_NAMES = {
    'info', 'thing', 'stuff', 'temp', 'tmp', 'val', 'obj', 'item',
    'foo', 'bar', 'baz', 'misc', 'blob', 'value',
}
MIN_NAME_LENGTH = 3


class IntentionRevealingNamesScanner(CodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in context.get('code_files', []):
            result = self._read_and_parse_file(Path(file_path))
            if result is None:
                continue
            content, lines, tree = result
            loop_targets = self._collect_loop_targets(tree)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    self._check_name(node.id, node, loop_targets, file_path, violations)
                elif isinstance(node, ast.arg):
                    if node.arg != 'self' and node.arg != 'cls':
                        self._check_name(node.arg, node, loop_targets, file_path, violations)
        return violations

    def _check_name(self, name, node, loop_targets, file_path, violations):
        lineno = getattr(node, 'lineno', 0)
        if name.startswith('_'):
            return
        if name.lower() in GENERIC_NAMES:
            violations.append({
                'rule': self.rule,
                'message': f"Name '{name}' is too generic. Use a domain-specific name.",
                'location': str(file_path),
                'line': lineno,
            })
            return
        if len(name) == 1 and name not in LOOP_VARS:
            violations.append({
                'rule': self.rule,
                'message': f"Single-letter name '{name}' hides intention.",
                'location': str(file_path),
                'line': lineno,
            })
        elif 1 < len(name) < MIN_NAME_LENGTH and name not in LOOP_VARS and (name, lineno) not in loop_targets:
            violations.append({
                'rule': self.rule,
                'message': f"Name '{name}' is very short ({len(name)} chars). Use a descriptive name.",
                'location': str(file_path),
                'line': lineno,
            })

    def _collect_loop_targets(self, tree) -> set:
        targets = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.AsyncFor)):
                if isinstance(node.target, ast.Name):
                    targets.add((node.target.id, node.target.lineno))
                elif isinstance(node.target, ast.Tuple):
                    for elt in node.target.elts:
                        if isinstance(elt, ast.Name):
                            targets.add((elt.id, elt.lineno))
        return targets


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(IntentionRevealingNamesScanner, 'use-intention-revealing-names')
