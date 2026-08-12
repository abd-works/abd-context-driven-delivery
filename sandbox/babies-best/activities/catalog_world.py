"""Shared domain world for Discover Nyc Activities acceptance helpers.

Sources: .context/discover-nyc-activities/scenarios; activities/; place/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from activities.activity import (
    KIND_EVENT,
    KIND_EVERGREEN,
    Activity,
    ActivityCatalog,
)
from place.place import Borough, PlaceFilter, RememberedPlace


@dataclass
class BabyProfile:
    age_band: str


@dataclass
class CatalogWorld:
    brooklyn: Borough = field(init=False)
    park_slope: object = field(init=False)
    staten_island: Borough = field(init=False)
    tottenville: object = field(init=False)
    playground: Activity = field(init=False)
    story_time: Activity = field(init=False)
    festival: Activity = field(init=False)
    catalog: ActivityCatalog = field(init=False)
    remembered: RememberedPlace = field(init=False)
    profile: BabyProfile = field(init=False)
    age_filter: str = field(init=False)
    kind_filter: Optional[str] = None
    place_filter: Optional[PlaceFilter] = None
    listed: list[Activity] = field(default_factory=list)
    detail: Optional[Activity] = None
    prompt_choose_place: bool = False
    empty_message: bool = False
    personal_lists: list[str] = field(default_factory=lambda: ["Weekend outings"])
    saved: list[str] = field(default_factory=list)
    prompt_create_list: bool = False

    def __post_init__(self) -> None:
        self.brooklyn = Borough(name="Brooklyn")
        self.park_slope = self.brooklyn.add_neighborhood("Park Slope")
        self.staten_island = Borough(name="Staten Island")
        self.tottenville = self.staten_island.add_neighborhood("Tottenville")
        self.playground = Activity(
            name="Carroll Park Playground",
            kind=KIND_EVERGREEN,
            age_band="6-12 months",
            neighborhood=self.park_slope,
            hours="dawn–dusk",
            notes="stroller-friendly paths",
        )
        self.story_time = Activity(
            name="Library Story Time",
            kind=KIND_EVENT,
            age_band="0-24 months",
            neighborhood=self.park_slope,
            event_date="this Saturday",
            event_time="10:00 am",
            notes="blankets on floor",
        )
        self.festival = Activity(
            name="Baby Music Festival",
            kind=KIND_EVENT,
            age_band="6-12 months",
            neighborhood=None,
            event_date="next Sunday",
            event_time="11:00 am",
        )
        self.catalog = ActivityCatalog(
            activities=[self.playground, self.story_time, self.festival]
        )
        self.remembered = RememberedPlace()
        self.profile = BabyProfile(age_band="6-12 months")
        self.age_filter = self.profile.age_band

    def open_things_to_do(self) -> None:
        restored = self.remembered.restore()
        if restored is None:
            self.place_filter = None
            self.listed = []
            self.prompt_choose_place = True
            self.empty_message = False
            return
        self.place_filter = restored
        self.prompt_choose_place = False
        self.refresh()

    def choose_place(self, borough: Borough, neighborhood_name: str) -> None:
        neighborhood = next(n for n in borough.neighborhoods if n.name == neighborhood_name)
        self.place_filter = PlaceFilter(
            borough=borough, neighborhood=neighborhood, include_citywide=False
        )
        self.remembered.remember(self.place_filter)
        self.prompt_choose_place = False
        self.refresh()

    def include_citywide(self, include: bool) -> None:
        assert self.place_filter is not None
        self.place_filter = self.place_filter.toggle_citywide(include)
        self.remembered.remember(self.place_filter)
        self.refresh()

    def filter_kind(self, kind: str) -> None:
        self.kind_filter = kind
        self.refresh()

    def override_age(self, age_band: str) -> None:
        self.age_filter = age_band
        self.refresh()

    def open_activity(self, name: str) -> Activity:
        self.detail = next(a for a in self.catalog.activities if a.name == name)
        return self.detail

    def save_to_list(self, list_name: str) -> None:
        assert self.detail is not None
        if not self.personal_lists:
            self.prompt_create_list = True
            return
        if list_name not in self.personal_lists:
            raise ValueError("unknown list")
        self.prompt_create_list = False
        self.saved.append(f"{list_name}:{self.detail.id}")

    def refresh(self) -> None:
        if self.place_filter is None:
            self.listed = []
            self.empty_message = False
            return
        self.listed = self.catalog.list_for(
            self.age_filter, self.place_filter, self.kind_filter
        )
        self.empty_message = len(self.listed) == 0
