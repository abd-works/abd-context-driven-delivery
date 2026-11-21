"""Clean Engineering's class model, as other practices and patterns reach it: the model, its modules and classes, their
operations, parameters, properties, invariants, and relationships, and how a name carries its stereotype marks and its
module path. A format's own classes are reached through the practice's ``formats``, never imported from here."""

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER, CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import joined_module_path, marks_in, module_path_in, stereotype_named, without_marks
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.operation import Operation, Parameter
from cdd_guidance.practices.clean_engineering.model.property import Invariant, Property
from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES
from cdd_guidance.practices.clean_engineering.model.type_refs import pascal_type_names

__all__ = [
    "CONSTRUCTOR_NAMES",
    "CleanEngineeringModel",
    "Invariant",
    "MODULE_FUNCTION_HOLDER",
    "Module",
    "OoadClass",
    "Operation",
    "Parameter",
    "Property",
    "Relationship",
    "joined_module_path",
    "marks_in",
    "module_path_in",
    "pascal_type_names",
    "stereotype_named",
    "without_marks",
]
