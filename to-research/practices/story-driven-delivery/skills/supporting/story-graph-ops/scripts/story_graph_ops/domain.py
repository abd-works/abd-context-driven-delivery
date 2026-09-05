from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Collaborator:
    name: str

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, name: str) -> 'Collaborator':
        return cls(name=name)

@dataclass
class Responsibility:
    name: str
    collaborators: List[Collaborator]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Responsibility':
        return cls(name=data.get('name', ''), collaborators=[Collaborator.from_str(c) for c in data.get('collaborators', [])])

    def to_dict(self) -> Dict[str, Any]:
        return {'name': self.name, 'collaborators': [c.name for c in self.collaborators]}

@dataclass
class DomainConcept:
    name: str
    responsibilities: List[Responsibility]
    realization: Optional[List[Dict[str, Any]]] = None  # Walkthrough/realization data
    module: Optional[str] = None
    inherits_from: Optional[str] = None
    _source_path: Optional[str] = None
    _extra_fields: Optional[Dict[str, Any]] = None  # Store any other fields not explicitly defined

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainConcept':
        # Extract known fields
        known_fields = {'name', 'responsibilities', 'realization', 'module', 'inherits_from', '_source_path'}
        extra_fields = {k: v for k, v in data.items() if k not in known_fields}
        
        return cls(
            name=data.get('name', ''),
            responsibilities=[Responsibility.from_dict(r) for r in data.get('responsibilities', [])],
            realization=data.get('realization'),  # Preserve realization field
            module=data.get('module'),
            inherits_from=data.get('inherits_from'),
            _source_path=data.get('_source_path'),
            _extra_fields=extra_fields if extra_fields else None
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {'name': self.name, 'responsibilities': [r.to_dict() for r in self.responsibilities]}
        # Preserve all optional fields if present
        if self.realization is not None:
            result['realization'] = self.realization
        if self.module is not None:
            result['module'] = self.module
        if self.inherits_from is not None:
            result['inherits_from'] = self.inherits_from
        if self._source_path is not None:
            result['_source_path'] = self._source_path
        # Preserve any extra fields
        if self._extra_fields:
            result.update(self._extra_fields)
        return result

@dataclass
class StoryUser:
    name: str

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, user_name: str) -> 'StoryUser':
        return cls(name=user_name)

    @classmethod
    def from_list(cls, user_names: List[str]) -> List['StoryUser']:
        return [cls.from_str(name) for name in user_names]

    def to_str(self) -> str:
        return str(self)