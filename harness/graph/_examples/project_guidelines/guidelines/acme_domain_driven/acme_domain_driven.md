## Overview

Acme's domain-driven stack. Each aggregate root saves and deletes itself; there are no repository classes.

## Guidance

A domain verb that does more than store is itself the save. Other aggregates come in through the constructor.

## Shared rules

- **`repository-is-crud`** — There is no repository. The root's own `save()` and `delete()` store it, and a domain verb that changes it saves it.
- **`root-saves-itself`** — Every aggregate root offers `save()` and `delete()` on the instance, and a static `all()` only where a screen lists them.
