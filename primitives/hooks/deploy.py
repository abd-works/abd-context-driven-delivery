"""Hook deploy metadata — re-export from ``dispatch``."""

from hooks.dispatch import (
    DISPATCH_SCRIPT,
    HookBinding,
    deploy_dispatch,
    hook_skill_sources,
)

__all__ = [
    "DISPATCH_SCRIPT",
    "HookBinding",
    "deploy_dispatch",
    "hook_skill_sources",
]
