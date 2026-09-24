"""Canonical Clean Engineering model types."""

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    OoadNode,
)
from practices.clean_engineering.model.field_types import OperationField, PropertyField, Relationship
from practices.clean_engineering.model.operation import Operation, Parameter
from practices.clean_engineering.model.property import Property
from practices.clean_engineering.model.update_report import ChildCollectionPair, UpdateReport

__all__ = [
    "ChildCollectionPair",
    "CleanEngineeringModel",
    "Module",
    "OoadClass",
    "OoadNode",
    "Operation",
    "OperationField",
    "Parameter",
    "Property",
    "PropertyField",
    "Relationship",
    "UpdateReport",
]
