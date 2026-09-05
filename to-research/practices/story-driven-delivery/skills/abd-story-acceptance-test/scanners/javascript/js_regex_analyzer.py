"""Regex-based JavaScript analyzer for files that can't be AST-parsed."""

import re
from typing import List, Tuple, Dict
from pathlib import Path


class JSRegexAnalyzer:
    """Fallback analyzer using regex when AST parsing fails."""
    
    @staticmethod
    def extract_functions(content: str, lines: List[str]) -> List[Tuple[str, int, int, str]]:
        """Extract functions using regex patterns.
        
        Returns:
            List of (name, start_line, end_line, type) tuples
        """
        functions = []
        brace_stack = []  # Stack of (type, name, start_line, brace_depth)
        current_depth = 0
        
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Count braces
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            # Check for function/method start (before updating depth)
            func_match = None
            func_type = None
            
            # Pattern 1: function name() {
            if re.search(r'\bfunction\s+(\w+)\s*\([^)]*\)\s*\{', line):
                match = re.search(r'\bfunction\s+(\w+)\s*\([^)]*\)\s*\{', line)
                func_match = match.group(1)
                func_type = 'function'
            
            # Pattern 2: const name = () => { or const name = function() {
            elif re.search(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{', line):
                match = re.search(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{', line)
                func_match = match.group(1)
                func_type = 'arrow'
            
            elif re.search(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\([^)]*\)\s*\{', line):
                match = re.search(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\([^)]*\)\s*\{', line)
                func_match = match.group(1)
                func_type = 'expression'
            
            # Pattern 3: Class methods - constructor, methodName()  
            #  Must be indented and followed by ( and {
            #  Exclude control structures (if, for, while, switch, catch)
            elif current_depth > 0 and re.match(r'^\s+(static\s+)?(\w+)\s*\([^)]*\)\s*\{', line):
                match = re.match(r'^\s+(static\s+)?(\w+)\s*\([^)]*\)\s*\{', line)
                method_name = match.group(2)
                
                # Skip control structures
                if method_name not in ('if', 'for', 'while', 'switch', 'catch', 'with'):
                    func_match = method_name
                    func_type = 'method'
            
            # If we found a function, push to stack
            if func_match and func_type and open_braces > 0:
                brace_stack.append((func_type, func_match, i, current_depth + 1))
            
            # Update depth
            current_depth += open_braces
            current_depth -= close_braces
            
            # Check if any functions ended
            while brace_stack and current_depth < brace_stack[-1][3]:
                func_type, func_name, start_line, expected_depth = brace_stack.pop()
                end_line = i
                functions.append((func_name, start_line, end_line, func_type))
        
        return functions
    
    @staticmethod
    def find_try_catch_blocks(lines: List[str]) -> List[Dict]:
        """Find try-catch blocks using regex."""
        blocks = []
        
        for i, line in enumerate(lines, start=1):
            # Match catch blocks
            if re.search(r'catch\s*\(', line):
                # Check if empty or only has console.log
                blocks.append({
                    'catch_line': i,
                    'line_text': line.strip()
                })
        
        return blocks
    
    @staticmethod
    def find_comments(lines: List[str]) -> List[Tuple[int, str, str]]:
        """Find comments in JavaScript code.
        
        Returns:
            List of (line_number, comment_text, comment_type) tuples
        """
        comments = []
        
        for i, line in enumerate(lines, start=1):
            # Single-line comments
            match = re.search(r'//\s*(.+)', line)
            if match:
                comments.append((i, match.group(1).strip(), 'line'))
            
            # Block comment start
            if '/*' in line:
                comments.append((i, line.strip(), 'block_start'))
        
        return comments
