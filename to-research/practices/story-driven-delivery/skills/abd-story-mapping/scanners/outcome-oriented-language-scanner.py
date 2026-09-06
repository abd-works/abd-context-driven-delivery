#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SKILLS = _ROOT.parent
for _p in (
    _SKILLS / 'execute-skill-using-skills-rules' / 'scripts',
    _SKILLS / 'story-graph-ops' / 'scripts',
    _ROOT / 'scanners',
):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

from scanner_runner import main_with_scanner  # noqa: E402

from typing import List, Dict, Any, Optional
from scanner_bases.violation import Violation
from story_map import Epic, Story, StoryNode, SubEpic
from story_scanner import StoryScanner

class OutcomeOrientedLanguageScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        if not node.name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_communication_verbs(node, node_type)
        if violation:
            violations.append(violation)
        
        violation = self._check_enablement_verbs(node, node_type)
        if violation:
            violations.append(violation)
        
        return violations
    
    def _get_node_type(self, node: StoryNode) -> str:
        name = node.name
        if isinstance(node, Epic):
            return 'epic'
        elif isinstance(node, SubEpic):
            return 'sub_epic'
        elif isinstance(node, Story):
            return 'story'
        return 'unknown'
    
    def _check_communication_verbs(self, node: StoryNode, node_type: str) -> Optional[Dict[str, Any]]:
        communication_verbs = ['showing', 'displaying', 'visualizing', 'presenting', 'rendering']
        return self._check_verb_usage(
            node, 
            node_type, 
            communication_verbs, 
            'communication',
            'Display … not Showing …'
        )
    
    def _check_enablement_verbs(self, node: StoryNode, node_type: str) -> Optional[Dict[str, Any]]:
        enablement_verbs = ['providing', 'enabling', 'allowing', 'supporting', 'facilitating']
        return self._check_verb_usage(
            node, 
            node_type, 
            enablement_verbs, 
            'enablement',
            'Load Configuration not Providing Configuration'
        )
    
    def _check_verb_usage(
        self, 
        node: StoryNode, 
        node_type: str, 
        verb_list: List[str], 
        verb_category: str,
        example: str
    ) -> Optional[Dict[str, Any]]:
        name = node.name
        name_lower = name.lower()
        words = name_lower.split()
        
        for word in words:
            if word in verb_list:
                location = node.map_location()
                return Violation(
                    rule=self.rule,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses {verb_category} verb "{word}" - use outcome verbs instead (e.g., "{example}")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None



if __name__ == '__main__':
    sys.exit(main_with_scanner(OutcomeOrientedLanguageScanner, rule_md_name='outcome-oriented-language'))
