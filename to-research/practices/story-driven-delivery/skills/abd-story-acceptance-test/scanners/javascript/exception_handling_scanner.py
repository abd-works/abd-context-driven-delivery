"""Scanner for detecting improper exception handling in JavaScript."""

from typing import List, Dict, Any
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanners.resources.violation import Violation
from scanner_bases.resources.scan_context import FileScanContext


class ExceptionHandlingScanner(JSCodeScanner):
    """Detects improper exception handling patterns in JavaScript code."""
    
    def scan_file_with_context(self, context: FileScanContext) -> List[Dict[str, Any]]:
        violations = []
        
        if not context.exists or not str(context.file_path).endswith('.js'):
            return violations
        
        parsed = self._parse_js_file(context.file_path)
        if not parsed:
            return violations
        
        content, ast, lines = parsed
        
        # Find all try-catch blocks
        try_blocks = self._find_try_catch_blocks(ast)
        
        for try_info in try_blocks:
            # Check for empty catch blocks
            if try_info['is_empty_catch']:
                violation = self._create_violation(
                    file_path=context.file_path,
                    line_number=try_info['catch_line'],
                    message="Empty catch block: Exceptions should be logged or handled, not silently swallowed",
                    details={'catch_line': try_info['catch_line']}
                )
                violations.append(violation)
            
            # Check for catch blocks that only have console.log
            if try_info['only_console_log']:
                violation = self._create_violation(
                    file_path=context.file_path,
                    line_number=try_info['catch_line'],
                    message="Catch block only contains console.log: Consider proper error handling or re-throwing",
                    details={'catch_line': try_info['catch_line']}
                )
                violations.append(violation)
            
            # Check for catch blocks without parameter (catch { })
            if try_info['no_param']:
                violation = self._create_violation(
                    file_path=context.file_path,
                    line_number=try_info['catch_line'],
                    message="Catch block without error parameter: Should capture and handle the error",
                    details={'catch_line': try_info['catch_line']}
                )
                violations.append(violation)
        
        return violations
    
    def _find_try_catch_blocks(self, ast: Dict) -> List[Dict]:
        """Find all try-catch blocks in the AST."""
        try_blocks = []
        
        def visit_node(node):
            if not isinstance(node, dict):
                return
            
            node_type = node.get('type')
            
            if node_type == 'TryStatement':
                handler = node.get('handler')
                if handler:
                    catch_info = self._analyze_catch_block(handler)
                    try_blocks.append(catch_info)
            
            # Recursively visit children
            for key, value in node.items():
                if isinstance(value, dict):
                    visit_node(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            visit_node(item)
        
        visit_node(ast)
        return try_blocks
    
    def _analyze_catch_block(self, handler: Dict) -> Dict:
        """Analyze a catch block for common issues."""
        catch_line = handler.get('loc', {}).get('start', {}).get('line', 0)
        param = handler.get('param')
        body = handler.get('body', {})
        body_statements = body.get('body', [])
        
        # Check if catch has no parameter
        no_param = param is None
        
        # Check if catch block is empty
        is_empty = len(body_statements) == 0
        
        # Check if only console.log
        only_console_log = False
        if len(body_statements) == 1:
            stmt = body_statements[0]
            if stmt.get('type') == 'ExpressionStatement':
                expr = stmt.get('expression', {})
                if expr.get('type') == 'CallExpression':
                    callee = expr.get('callee', {})
                    if (callee.get('type') == 'MemberExpression' and
                        callee.get('object', {}).get('name') == 'console' and
                        callee.get('property', {}).get('name') == 'log'):
                        only_console_log = True
        
        return {
            'catch_line': catch_line,
            'is_empty_catch': is_empty,
            'only_console_log': only_console_log,
            'no_param': no_param
        }
