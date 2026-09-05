"""Scanner for checking naming convention consistency in JavaScript."""

from typing import List, Dict, Any, Set
from pathlib import Path
import re
from js_code_scanner import JSCodeScanner
from scanners.resources.violation import Violation
from scanner_bases.resources.scan_context import FileScanContext


class ConsistentNamingScanner(JSCodeScanner):
    """Ensures naming conventions are consistent across JavaScript code."""
    
    def scan_file_with_context(self, context: FileScanContext) -> List[Dict[str, Any]]:
        violations = []
        
        if not context.exists or not str(context.file_path).endswith('.js'):
            return violations
        
        parsed = self._parse_js_file(context.file_path)
        if not parsed:
            return violations
        
        content, ast, lines = parsed
        
        # Extract all identifiers and their naming styles
        identifiers = self._extract_identifiers(ast)
        
        # Check for inconsistent naming
        naming_violations = self._check_naming_consistency(identifiers, context.file_path)
        violations.extend(naming_violations)
        
        return violations
    
    def _extract_identifiers(self, ast: Dict) -> Dict[str, List[Dict]]:
        """Extract all identifiers categorized by type."""
        identifiers = {
            'functions': [],
            'variables': [],
            'classes': [],
            'methods': []
        }
        
        def visit_node(node, context_type=None):
            if not isinstance(node, dict):
                return
            
            node_type = node.get('type')
            
            # Function declarations
            if node_type == 'FunctionDeclaration':
                name = node.get('id', {}).get('name')
                line = node.get('loc', {}).get('start', {}).get('line', 0)
                if name:
                    identifiers['functions'].append({
                        'name': name,
                        'line': line,
                        'style': self._detect_naming_style(name)
                    })
            
            # Variable declarations
            elif node_type == 'VariableDeclarator':
                name = node.get('id', {}).get('name')
                line = node.get('loc', {}).get('start', {}).get('line', 0)
                if name:
                    identifiers['variables'].append({
                        'name': name,
                        'line': line,
                        'style': self._detect_naming_style(name)
                    })
            
            # Class declarations
            elif node_type == 'ClassDeclaration':
                name = node.get('id', {}).get('name')
                line = node.get('loc', {}).get('start', {}).get('line', 0)
                if name:
                    identifiers['classes'].append({
                        'name': name,
                        'line': line,
                        'style': self._detect_naming_style(name)
                    })
                # Visit class body for methods
                body = node.get('body', {}).get('body', [])
                for item in body:
                    if item.get('type') == 'MethodDefinition':
                        method_name = item.get('key', {}).get('name')
                        method_line = item.get('loc', {}).get('start', {}).get('line', 0)
                        if method_name and method_name != 'constructor':
                            identifiers['methods'].append({
                                'name': method_name,
                                'line': method_line,
                                'style': self._detect_naming_style(method_name)
                            })
            
            # Recursively visit children
            for key, value in node.items():
                if isinstance(value, dict):
                    visit_node(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            visit_node(item)
        
        visit_node(ast)
        return identifiers
    
    def _detect_naming_style(self, name: str) -> str:
        """Detect the naming convention used."""
        if re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
            return 'PascalCase'
        elif re.match(r'^[a-z][a-zA-Z0-9]*$', name):
            return 'camelCase'
        elif re.match(r'^[a-z][a-z0-9_]*$', name):
            return 'snake_case'
        elif re.match(r'^[A-Z][A-Z0-9_]*$', name):
            return 'SCREAMING_SNAKE_CASE'
        elif re.match(r'^[a-z][a-z0-9-]*$', name):
            return 'kebab-case'
        else:
            return 'mixed'
    
    def _check_naming_consistency(self, identifiers: Dict, file_path: Path) -> List[Dict[str, Any]]:
        """Check for naming convention violations."""
        violations = []
        
        # Classes should be PascalCase
        for class_info in identifiers['classes']:
            if class_info['style'] != 'PascalCase':
                violation = self._create_violation(
                    file_path=file_path,
                    line_number=class_info['line'],
                    message=f"Class '{class_info['name']}' should use PascalCase, found {class_info['style']}",
                    details={
                        'name': class_info['name'],
                        'expected': 'PascalCase',
                        'actual': class_info['style']
                    }
                )
                violations.append(violation)
        
        # Functions and variables should be camelCase
        for func_info in identifiers['functions']:
            if func_info['style'] not in ('camelCase', 'PascalCase'):
                violation = self._create_violation(
                    file_path=file_path,
                    line_number=func_info['line'],
                    message=f"Function '{func_info['name']}' should use camelCase, found {func_info['style']}",
                    details={
                        'name': func_info['name'],
                        'expected': 'camelCase',
                        'actual': func_info['style']
                    }
                )
                violations.append(violation)
        
        # Check for mixed styles in variables
        var_styles = set(v['style'] for v in identifiers['variables'] if v['style'] in ('camelCase', 'snake_case'))
        if len(var_styles) > 1:
            # Find offending variables
            for var_info in identifiers['variables']:
                if var_info['style'] == 'snake_case':
                    violation = self._create_violation(
                        file_path=file_path,
                        line_number=var_info['line'],
                        message=f"Variable '{var_info['name']}' uses snake_case; JavaScript convention is camelCase",
                        details={
                            'name': var_info['name'],
                            'expected': 'camelCase',
                            'actual': 'snake_case'
                        }
                    )
                    violations.append(violation)
        
        return violations
