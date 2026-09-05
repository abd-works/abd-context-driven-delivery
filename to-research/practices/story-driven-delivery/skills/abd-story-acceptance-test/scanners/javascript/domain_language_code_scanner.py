"""Scanner for domain language in JavaScript/TypeScript code (client and server).
Equivalent to Python DomainLanguageCodeScanner: class/function/param names should use domain terms.
"""

import re
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext


class DomainLanguageCodeScanner(JSCodeScanner):
    """Detects domain language violations in JavaScript/TypeScript.
    Same rules as Python: use domain terms from specification; avoid generate_/calculate_;
    builder-class exception for class names ending in Generator, Calculator, etc.
    """

    GENERATE_PATTERNS = [r'^generate_', r'^calculate_']
    BUILDER_VERB_SUFFIXES = (
        'Generator', 'Calculator', 'Builder', 'Processor',
        'Handler', 'Factory', 'Creator', 'Producer', 'Compiler'
    )
    GENERIC_NAMES = {
        'self', 'result', 'value', 'data', 'item', 'obj', 'workspace', 'root', 'path', 'config',
        'ctx', 'req', 'res', 'err', 'cb', 'fn', 'options', 'opts', 'args', 'e', 'i', 'j'
    }

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not (path_str.endswith('.js') or path_str.endswith('.ts') or path_str.endswith('.mjs') or path_str.endswith('.cjs')):
            return violations
        file_path = context.file_path
        story_graph = getattr(context, 'story_graph', None) or {}
        domain_terms = self._extract_domain_terms(story_graph)
        parsed = self._parse_js_file(file_path)
        if not parsed:
            return violations
        content, ast, lines = parsed
        if not isinstance(ast, dict):
            return violations
        if ast.get('_fallback') or not ast.get('body'):
            classes, functions = self._extract_classes_and_functions_regex(lines)
        else:
            classes, functions = self._extract_classes_and_functions_ast(ast)
        for class_name, line_no in classes:
            vs = self._check_class_domain_language(class_name, file_path, line_no, domain_terms)
            violations.extend(vs)
        for (name, line_no, param_names, enclosing_class) in functions:
            vs = self._check_function_domain_language(
                name, line_no, param_names, file_path, domain_terms, enclosing_class
            )
            violations.extend(vs)
        return violations

    def _is_builder_class_with_domain_prefix(self, class_name: Optional[str]) -> bool:
        if not class_name:
            return False
        for suffix in self.BUILDER_VERB_SUFFIXES:
            if class_name.endswith(suffix):
                prefix = class_name[:-len(suffix)]
                if prefix:
                    return True
        return False

    def _matches_domain_term(self, name: str, domain_terms: set) -> bool:
        if not name or not domain_terms:
            return False
        name_lower = name.lower()
        words = set(re.findall(r'\b[a-zA-Z]+\b', name_lower))
        for term in domain_terms:
            if term in words or term in name_lower or name_lower in term:
                return True
        return False

    def _check_class_domain_language(
        self, class_name: str, file_path: Path, line_no: int, domain_terms: set
    ) -> List[Dict[str, Any]]:
        violations = []
        if class_name.lower() in self.GENERIC_NAMES:
            return violations
        if domain_terms and not self._matches_domain_term(class_name, domain_terms):
            sample = ', '.join(sorted(domain_terms)[:10])
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    f'Class "{class_name}" doesn\'t match domain terms. '
                    f'Use domain-specific language from specification: {sample}...'
                ),
                location=str(file_path),
                line_number=line_no,
                severity='info'
            ).to_dict())
        return violations

    def _check_function_domain_language(
        self,
        func_name: str,
        line_no: int,
        param_names: List[str],
        file_path: Path,
        domain_terms: set,
        enclosing_class: Optional[str]
    ) -> List[Dict[str, Any]]:
        violations = []
        skip_generate = self._is_builder_class_with_domain_prefix(enclosing_class)
        if not skip_generate:
            for pattern in self.GENERATE_PATTERNS:
                if re.search(pattern, func_name.lower()):
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Function "{func_name}" uses generate/calculate. '
                            'Use property instead (e.g., "recommended_trades" not "generate_recommendation").'
                        ),
                        location=str(file_path),
                        line_number=line_no,
                        severity='warning'
                    ).to_dict())
        if domain_terms and func_name.lower() not in self.GENERIC_NAMES and not self._matches_domain_term(func_name, domain_terms):
            sample = ', '.join(sorted(domain_terms)[:10])
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    f'Function "{func_name}" doesn\'t match domain terms. '
                    f'Use domain-specific language from specification: {sample}...'
                ),
                location=str(file_path),
                line_number=line_no,
                severity='info'
            ).to_dict())
        for arg in param_names:
            if arg.lower() in self.GENERIC_NAMES:
                continue
            if domain_terms and not self._matches_domain_term(arg, domain_terms):
                sample = ', '.join(sorted(domain_terms)[:10])
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Function "{func_name}" uses parameter name "{arg}" that doesn\'t match domain terms. '
                        f'Use domain-specific language: {sample}...'
                    ),
                    location=str(file_path),
                    line_number=line_no,
                    severity='info'
                ).to_dict())
        return violations

    def _extract_classes_and_functions_ast(self, ast: Dict) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int, List[str], Optional[str]]]]:
        classes = []
        functions = []
        current_class = [None]

        def param_names_from_params(params: List) -> List[str]:
            names = []
            for p in params or []:
                if isinstance(p, dict):
                    name = p.get('name') or (p.get('id') or {}).get('name')
                    if name:
                        names.append(name)
            return names

        def visit(node, parent_name=None, enclosing_class=None):
            if not isinstance(node, dict):
                return
            t = node.get('type')
            loc = node.get('loc', {})
            line = loc.get('start', {}).get('line', 1)
            if t == 'ClassDeclaration':
                name = (node.get('id') or {}).get('name', '')
                if name:
                    classes.append((name, line))
                    prev = current_class[0]
                    current_class[0] = name
                    for key, value in (node.get('body') or {}).items():
                        if key == 'body' and isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    visit(item, enclosing_class=name)
                    current_class[0] = prev
                return
            if t == 'MethodDefinition':
                name = (node.get('key') or {}).get('name', '')
                val = node.get('value', {})
                params = val.get('params', [])
                names = param_names_from_params(params)
                if name:
                    functions.append((name, line, names, current_class[0]))
                return
            if t == 'FunctionDeclaration':
                name = (node.get('id') or {}).get('name', '<anonymous>')
                params = node.get('params', [])
                names = param_names_from_params(params)
                functions.append((name, line, names, current_class[0]))
                return
            if t == 'VariableDeclarator':
                var_name = (node.get('id') or {}).get('name')
                init = node.get('init')
                if init and isinstance(init, dict):
                    it = init.get('type')
                    if it == 'ArrowFunctionExpression' or it == 'FunctionExpression':
                        params = init.get('params', [])
                        names = param_names_from_params(params)
                        functions.append((var_name or '<anonymous>', line, names, current_class[0]))
                if var_name:
                    visit(init, parent_name=var_name, enclosing_class=current_class[0])
                return
            for key, value in node.items():
                if isinstance(value, dict):
                    visit(value, enclosing_class=current_class[0])
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            visit(item, enclosing_class=current_class[0])

        visit(ast)
        return classes, functions

    def _extract_classes_and_functions_regex(self, lines: List[str]) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int, List[str], Optional[str]]]]:
        classes = []
        functions = []
        from js_regex_analyzer import JSRegexAnalyzer
        funcs = JSRegexAnalyzer.extract_functions('\n'.join(lines), lines)
        for name, start_line, end_line, ftype in funcs:
            param_names = self._extract_params_from_line(lines[start_line - 1] if start_line <= len(lines) else '')
            functions.append((name, start_line, param_names, None))
        for i, line in enumerate(lines, 1):
            m = re.search(r'\bclass\s+(\w+)\s*[\{:]', line)
            if m:
                classes.append((m.group(1), i))
        return classes, functions

    def _extract_params_from_line(self, line: str) -> List[str]:
        m = re.search(r'\(\s*([^)]*)\s*\)', line)
        if not m:
            return []
        inner = m.group(1).strip()
        if not inner:
            return []
        return [p.strip().split('=')[0].strip().lstrip('...') for p in re.split(r',', inner) if p.strip()]
