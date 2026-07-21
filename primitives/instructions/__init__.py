"""Instruction values, path routing, and @instruction slots."""
from .instructions import (
    Instruction,
    InstructionHost,
    _FORMAT_TEMPLATE_EXT,
    _active_resource,
    _expand_docstring,
    _format_keys,
    _inline,
    _is_framework_action,
    _path_for_name,
    _path_for_template,
    _path_for_templates,
    _slug_variants,
    instruction,
    instruction_slot_names,
)

__all__ = [
    "Instruction",
    "InstructionHost",
    "instruction",
    "instruction_slot_names",
    "_FORMAT_TEMPLATE_EXT",
    "_active_resource",
    "_expand_docstring",
    "_format_keys",
    "_inline",
    "_is_framework_action",
    "_path_for_name",
    "_path_for_template",
    "_path_for_templates",
    "_slug_variants",
]
