"""Scanner for detecting JavaScript functions that are too large."""

from typing import List, Dict, Any
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanners.resources.violation import Violation
from scanner_bases.resources.scan_context import FileScanContext


class FunctionSizeScanner(JSCodeScanner):
    """Detects functions that exceed size limits in JavaScript code."""
    
    MAX_FUNCTION_LINES = 20  # Recommended maximum lines per function
    
    def scan_file_with_context(self, context: FileScanContext) -> List[Dict[str, Any]]:
        violations = []
        
        if not context.exists or not context.file_path:
            return violations
        
        # Only scan JavaScript files
        if not str(context.file_path).endswith('.js'):
            return violations
        
        parsed = self._parse_js_file(context.file_path)
        if not parsed:
            return violations
        
        content, ast, lines = parsed
        
        # Safety check for ast
        if not ast or not isinstance(ast, dict):
            return violations
        
        # Check if we need to use regex fallback
        if ast.get('_fallback') or len(ast.get('body', [])) == 0:
            # Use regex-based function extraction
            from js_regex_analyzer import JSRegexAnalyzer
            functions = JSRegexAnalyzer.extract_functions(content, lines)
        else:
            # Extract all functions from AST
            functions = self._extract_all_functions(ast, lines)
        
        # Check each function's size
        for func_info in functions:
            # Safety check
            if not func_info or len(func_info) < 4:
                continue
            
            func_name, start_line, end_line, func_type = func_info
            
            # Skip if invalid line numbers
            if not start_line or not end_line or end_line < start_line:
                continue
            
            func_lines = end_line - start_line + 1
            
            if func_lines > self.MAX_FUNCTION_LINES:
                violation = self._create_violation(
                    file_path=context.file_path,
                    line_number=start_line,
                    message=f"Function '{func_name}' is {func_lines} lines (max: {self.MAX_FUNCTION_LINES})",
                    details={
                        'function_name': func_name,
                        'function_type': func_type,
                        'actual_lines': func_lines,
                        'max_lines': self.MAX_FUNCTION_LINES,
                        'start_line': start_line,
                        'end_line': end_line
                    }
                )
                violations.append(violation)
        
        return violations
    
    def _extract_all_functions(self, ast: Dict, lines: List[str]) -> List[tuple]:
        """Extract all function definitions from JavaScript AST.
        
        Returns:
            List of (name, start_line, end_line, type) tuples
        """
        functions = []
        
        def visit_node(node, parent_name=None):
            if not isinstance(node, dict):
                return
            
            node_type = node.get('type')
            
            # Function Declaration: function foo() {}
            if node_type == 'FunctionDeclaration':
                id_node = node.get('id') or {}
                name = id_node.get('name', '<anonymous>') if isinstance(id_node, dict) else '<anonymous>'
                loc = node.get('loc', {})
                start = loc.get('start', {}).get('line', 0)
                end = loc.get('end', {}).get('line', 0)
                functions.append((name, start, end, 'function'))
            
            # Arrow Function: const foo = () => {}
            elif node_type == 'ArrowFunctionExpression':
                # Get name from parent VariableDeclarator if available
                name = parent_name or '<arrow>'
                loc = node.get('loc', {})
                start = loc.get('start', {}).get('line', 0)
                end = loc.get('end', {}).get('line', 0)
                functions.append((name, start, end, 'arrow'))
            
            # Function Expression: const foo = function() {}
            elif node_type == 'FunctionExpression':
                # Try to get name from function itself or parent (id may be None)
                id_node = node.get('id') or {}
                name = id_node.get('name') if isinstance(id_node, dict) else None
                name = name or parent_name or '<anonymous>'
                loc = node.get('loc', {})
                start = loc.get('start', {}).get('line', 0)
                end = loc.get('end', {}).get('line', 0)
                functions.append((name, start, end, 'expression'))
            
            # Method Definition: class X { method() {} }
            elif node_type == 'MethodDefinition':
                key_node = node.get('key') or {}
                name = key_node.get('name', '<method>') if isinstance(key_node, dict) else '<method>'
                func_node = node.get('value', {})
                loc = func_node.get('loc', {})
                start = loc.get('start', {}).get('line', 0)
                end = loc.get('end', {}).get('line', 0)
                functions.append((name, start, end, 'method'))
            
            # Variable Declarator: const foo = ... (pass name to children)
            elif node_type == 'VariableDeclarator':
                id_node = node.get('id') or {}
                var_name = id_node.get('name') if isinstance(id_node, dict) else None
                if var_name:
                    visit_node(node.get('init'), var_name)
                    return
            
            # Recursively visit all child nodes
            for key, value in node.items():
                if isinstance(value, dict):
                    visit_node(value, parent_name)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            visit_node(item, parent_name)
        
        visit_node(ast)
        return functions
