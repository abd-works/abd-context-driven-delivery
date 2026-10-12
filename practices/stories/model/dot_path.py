"""Yamale check that id is the dot path of text slugs from the root to this node."""

import re

from yamale.validators import DefaultValidators, Validator


class DotPath(Validator):
    """'Get Payment' under 'Enter Payment' under 'Onboard A Customer' is onboard-a-customer.enter-payment.get-payment."""

    tag = "dotPath"

    def _is_valid(self, value):
        text = _field(value, "text")
        if not isinstance(text, str) or not text.strip():
            return False
        return _field(value, "id") == dot_path(value)

    def fail(self, value):
        found = _field(value, "id")
        return "id '%s' is not the dot path '%s'." % (found, dot_path(value))


def dot_path(node):
    """Root slug, then each child slug, joined by dots."""
    slugs = []
    seen = set()
    current = node
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        slugs.append(text_slug(_field(current, "text")))
        current = _field(current, "belongsTo")
    slugs.reverse()
    return ".".join(slugs)


def text_slug(text):
    parts = re.findall(r"[A-Za-z0-9]+", text or "")
    return "-".join(part.lower() for part in parts)


def _field(node, name):
    if isinstance(node, dict):
        return node.get(name)
    return getattr(node, name, None)


def validators():
    """Yamale's built-in validators plus dotPath()."""
    registered = DefaultValidators.copy()
    registered[DotPath.tag] = DotPath
    return registered
