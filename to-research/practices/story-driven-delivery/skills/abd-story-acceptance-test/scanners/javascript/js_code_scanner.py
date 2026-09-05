"""Base scanner for JavaScript code validation."""

from abc import abstractmethod
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
import json
import subprocess
from scanner_bases.scanner import Scanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import ScanFilesContext, FileScanContext, CrossFileScanContext
    from actions.rules.rule import Rule


class JSCodeScanner(Scanner):
    """Base class for JavaScript code scanners.
    
    Uses esprima (via Node.js) to parse JavaScript and provide AST analysis.
    Subclasses implement specific validation rules.
    """
    
    def __init__(self, rule: 'Rule'):
        super().__init__(rule)
        self.story_graph = None
    
    def scan_with_context(self, context: 'ScanFilesContext') -> List[Dict[str, Any]]:
        self.story_graph = context.story_graph
        return super().scan_with_context(context)
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        self.story_graph = context.story_graph
        return self._empty_violation_list()
    
    def _parse_js_file(self, file_path: Path) -> Optional[Tuple[str, Dict, List[str]]]:
        """Parse a JavaScript file and return (content, AST, lines).
        
        Returns:
            Tuple of (file_content, ast_dict, lines_list) or None if parsing fails
        """
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Try AST parsing first
            ast = self._parse_js_with_esprima(content, str(file_path))
            
            if ast is None:
                # Fallback: return placeholder AST for regex-based analysis
                ast = {'type': 'Program', 'body': [], '_fallback': True}
            
            return (content, ast, lines)
        
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            return None
    
    def _parse_js_with_esprima(self, content: str, filename: str) -> Optional[Dict]:
        """Use esprima (via Node.js) to parse JavaScript code.
        
        Returns:
            AST dictionary or None if parsing fails
        """
        import tempfile
        import os
        
        try:
            # Write content to temp file (avoids stdin encoding issues)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', encoding='utf-8', delete=False) as f:
                temp_path = f.name
                f.write(content)
            
            try:
                # Create a Node.js script that reads from file
                js_script = f"""
                const esprima = require('esprima');
                const fs = require('fs');
                
                const content = fs.readFileSync('{temp_path.replace(chr(92), chr(92)+chr(92))}', 'utf-8');
                
                try {{
                    // Try as module first (supports more modern syntax)
                    const ast = esprima.parseModule(content, {{
                        loc: true,
                        range: true,
                        comment: true,
                        tolerant: true
                    }});
                    console.log(JSON.stringify(ast));
                }} catch (e) {{
                    // Fall back to script mode
                    try {{
                        const ast = esprima.parseScript(content, {{
                            loc: true,
                            range: true,
                            comment: true,
                            tolerant: true
                        }});
                        console.log(JSON.stringify(ast));
                    }} catch (e2) {{
                        console.error('Parse error:', e2.message);
                        process.exit(1);
                    }}
                }}
                """
                
                # Run Node.js with the script
                result = subprocess.run(
                    ['node', '-e', js_script],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=30
                )
                
                if result.returncode != 0:
                    return None
                
                ast = json.loads(result.stdout)
                return ast
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _extract_domain_terms(self, story_graph: Dict[str, Any]) -> set:
        """Extract domain terminology from story graph."""
        domain_terms = self._get_common_domain_terms()
        
        if not story_graph:
            return domain_terms
        
        for epic in story_graph.get('epics', []):
            if isinstance(epic, dict):
                self._extract_terms_from_epic(epic, domain_terms)
        
        return domain_terms
    
    def _get_common_domain_terms(self) -> set:
        """Get common technical terms that aren't domain-specific."""
        return {
            'json', 'data', 'param', 'params', 'parameter', 'parameters',
            'var', 'vars', 'variable', 'variables',
            'method', 'methods', 'class', 'classes', 'call', 'calls',
            'config', 'configuration', 'configurations',
            'function', 'const', 'let', 'return', 'async', 'await',
            'promise', 'callback', 'event', 'listener',
            'element', 'node', 'component', 'props', 'state',
            'agent', 'bot', 'workflow', 'story', 'epic', 'scenario', 'action',
            'behavior', 'rule', 'rules', 'validation', 'validate', 'scanner',
            'file', 'files', 'directory', 'directories', 'path', 'paths',
            'tool', 'tools', 'server', 'catalog', 'metadata'
        }
    
    def _extract_terms_from_epic(self, epic: dict, domain_terms: set) -> None:
        self._add_name_terms(epic.get('name', ''), domain_terms)
        self._extract_terms_from_concepts(epic.get('domain_concepts', []), domain_terms)
        
        for sub_epic in epic.get('sub_epics', []):
            if isinstance(sub_epic, dict):
                self._extract_terms_from_sub_epic(sub_epic, domain_terms)
    
    def _extract_terms_from_sub_epic(self, sub_epic: dict, domain_terms: set) -> None:
        self._add_name_terms(sub_epic.get('name', ''), domain_terms)
        self._extract_terms_from_concepts(sub_epic.get('domain_concepts', []), domain_terms)
        
        for story_group in sub_epic.get('story_groups', []):
            if isinstance(story_group, dict):
                for story in story_group.get('stories', []):
                    if isinstance(story, dict):
                        self._extract_terms_from_story(story, domain_terms)
    
    def _extract_terms_from_concepts(self, concepts: list, domain_terms: set) -> None:
        for concept in concepts:
            if not isinstance(concept, dict):
                continue
            
            concept_name = concept.get('name', '')
            if concept_name:
                domain_terms.add(concept_name.lower())
                domain_terms.add(concept_name.lower().replace(' ', '_'))
                domain_terms.update(self._extract_words_from_text(concept_name))
            
            self._extract_responsibility_terms(concept.get('responsibilities', []), domain_terms)
            self._extract_collaborator_terms(concept.get('collaborators', []), domain_terms)
    
    def _extract_responsibility_terms(self, responsibilities: list, domain_terms: set) -> None:
        for resp in responsibilities:
            if isinstance(resp, dict) and resp.get('name'):
                domain_terms.update(self._extract_words_from_text(resp['name']))
    
    def _extract_collaborator_terms(self, collaborators: list, domain_terms: set) -> None:
        for collab in collaborators:
            if isinstance(collab, str):
                domain_terms.add(collab.lower())
                domain_terms.update(self._extract_words_from_text(collab))
    
    def _extract_terms_from_story(self, story: dict, domain_terms: set) -> None:
        self._add_name_terms(story.get('name', ''), domain_terms)
        self._extract_acceptance_criteria_terms(story.get('acceptance_criteria', []), domain_terms)
        self._extract_scenario_terms(story.get('scenarios', []), domain_terms)
    
    def _extract_acceptance_criteria_terms(self, criteria: list, domain_terms: set) -> None:
        for ac in criteria:
            if isinstance(ac, dict):
                domain_terms.update(self._extract_words_from_text(ac.get('description', '')))
    
    def _extract_scenario_terms(self, scenarios: list, domain_terms: set) -> None:
        for scenario in scenarios:
            if isinstance(scenario, dict):
                self._add_name_terms(scenario.get('name', ''), domain_terms)
    
    def _add_name_terms(self, name: str, domain_terms: set) -> None:
        if name:
            domain_terms.update(self._extract_words_from_text(name))
    
    def _extract_words_from_text(self, text: str) -> set:
        """Extract individual words from text."""
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        return {w for w in words if len(w) > 2}
    
    def _create_violation(
        self,
        file_path: Path,
        line_number: int,
        message: str,
        details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a violation dictionary (legacy format with file key)."""
        violation = {
            'file': str(file_path),
            'line_number': line_number,
            'violation_message': message,
            'rule_name': self.rule.name if hasattr(self, 'rule') and self.rule else 'unknown'
        }
        if details:
            violation['details'] = details
        return violation

    def _violation_to_dict(
        self,
        violation_message: str,
        file_path: Path,
        line_number: Optional[int] = None,
        severity: str = 'warning'
    ) -> Dict[str, Any]:
        """Create a violation dict using scanners.violation.Violation (same format as Python scanners)."""
        return Violation(
            rule=self.rule,
            violation_message=violation_message,
            line_number=line_number,
            location=str(file_path) if file_path else None,
            severity=severity
        ).to_dict()
