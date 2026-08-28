"""
# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
# invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from place.place import Neighborhood, PlaceFilter


KIND_EVERGREEN = "evergreen"
KIND_EVENT = "event"
KIND_PLACES = "Places"
KIND_EVENTS = "Events"


class IActivity(ABC):
    id: str
    name: str
    kind: str
    age_band: str
    neighborhood: Optional[Neighborhood]
    hours: Optional[str]
    event_date: Optional[str]
    event_time: Optional[str]
    notes: Optional[str]

    @abstractmethod
    def matches_age(self, age_band: str) -> bool:
        ...

    @abstractmethod
    def matches_place(self, place_filter: PlaceFilter) -> bool:
        ...

    @abstractmethod
    def matches_kind(self, kind_filter: Optional[str]) -> bool:
        ...

    @abstractmethod
    def place_label(self) -> str:
        ...


class IActivityCatalog(ABC):
    @abstractmethod
    def list_for(
        self,
        age_band: str,
        place_filter: PlaceFilter,
        kind_filter: Optional[str] = None,
    ) -> list[IActivity]:
        ...


class IActivityRepository(ABC):
    @abstractmethod
    def add(self, activity: IActivity) -> None:
        ...

    @abstractmethod
    def find_by_id(self, activity_id: str) -> Optional[IActivity]:
        ...

    @abstractmethod
    def all(self) -> list[IActivity]:
        ...


@dataclass
class Activity:
    name: str
    kind: str
    age_band: str
    neighborhood: Optional[Neighborhood] = None
    hours: Optional[str] = None
    event_date: Optional[str] = None
    event_time: Optional[str] = None
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if self.kind not in (KIND_EVERGREEN, KIND_EVENT):
            raise ValueError("kind must be evergreen or event")

    def matches_age(self, age_band: str) -> bool:
        return self.age_band == age_band

    def matches_place(self, place_filter: PlaceFilter) -> bool:
        # Citywide: no neighborhood on the activity
        if self.neighborhood is None:
            return place_filter.include_citywide
        if place_filter.neighborhood is not None:
            return self.neighborhood.id == place_filter.neighborhood.id
        if place_filter.borough is not None:
            return self.neighborhood.borough.id == place_filter.borough.id
        return False

    def matches_kind(self, kind_filter: Optional[str]) -> bool:
        if kind_filter is None or kind_filter in ("", "All"):
            return True
        if kind_filter == KIND_PLACES:
            return self.kind == KIND_EVERGREEN
        if kind_filter == KIND_EVENTS:
            return self.kind == KIND_EVENT
        return self.kind == kind_filter

    def place_label(self) -> str:
        if self.neighborhood is None:
            return "Citywide"
        return f"{self.neighborhood.borough.name} / {self.neighborhood.name}"


@dataclass
class ActivityCatalog:
    activities: list[Activity]

    def list_for(
        self,
        age_band: str,
        place_filter: PlaceFilter,
        kind_filter: Optional[str] = None,
    ) -> list[Activity]:
        return [
            activity
            for activity in self.activities
            if activity.matches_age(age_band)
            and activity.matches_place(place_filter)
            and activity.matches_kind(kind_filter)
        ]


@dataclass
class ActivityRepository:
    _items: dict[str, Activity] = field(default_factory=dict)

    def add(self, activity: Activity) -> None:
        self._items[activity.id] = activity

    def find_by_id(self, activity_id: str) -> Optional[Activity]:
        return self._items.get(activity_id)

    def all(self) -> list[Activity]:
        return list(self._items.values())
