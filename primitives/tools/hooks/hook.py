"""Backward-compatible re-export — prefer ``hooks.hook``."""
from hooks.hook import CURSOR_EVENTS, Hook, HookHarness, hook

__all__ = ["CURSOR_EVENTS", "Hook", "HookHarness", "hook"]
