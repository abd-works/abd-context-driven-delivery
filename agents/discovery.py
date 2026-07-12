"""Discover @action members on a toolset instance."""
from __future__ import annotations

import inspect

from agents.action import Action
from tools.tool import Toolset


def discover_actions(instance: Toolset) -> dict[str, Action]:
    discovered: dict[str, Action] = {}
    for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
        if getattr(member, "_is_action", False):
            discovered[name] = Action(name=name, callable=getattr(instance, name))
    return discovered


def has_actions(instance: Toolset) -> bool:
    return bool(discover_actions(instance))
