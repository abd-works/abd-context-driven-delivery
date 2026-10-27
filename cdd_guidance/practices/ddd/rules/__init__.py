"""DDD graph rule classes."""

from cdd_guidance.practices.ddd.rules.tactical import (
    EveryClassCarriesDddStereotype,
    DomainConceptsNotTechnicalNames,
    FlaccidDataObject,
    LoadWithIdentityInHand,
    NoOrphanedObjects,
    PrivateMethodNaming,
    RepositoryIsCollectionLifecycle,
    ScreenInterfaceNotADomainObject,
    ServiceIsHomeless,
)

RULES: tuple = (
    PrivateMethodNaming(),
    FlaccidDataObject(),
    EveryClassCarriesDddStereotype(),
    DomainConceptsNotTechnicalNames(),
    ServiceIsHomeless(),
    RepositoryIsCollectionLifecycle(),
    LoadWithIdentityInHand(),
    NoOrphanedObjects(),
    ScreenInterfaceNotADomainObject(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
