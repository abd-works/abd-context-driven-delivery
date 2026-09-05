# pml-midtier Express Architecture Specification

## Table of Contents

- [Overview](#overview)
- [Mechanisms](#mechanisms)
- [Testing Architecture](#testing-architecture)
- [References](#references)

---

## Overview

pml-midtier is a Node.js/Express API gateway sitting between the Paradise Mobile consumer apps and the downstream systems.

---

## Mechanisms

**Configuration & Secrets** (`src/configs/`) -- loads `.env` once before any module runs. [src/configs/](/src/configs/architecture-context.md)

**Authentication** (`src/middlewares/Auth/`) -- Cognito JWT validation. [src/middlewares/Auth/](/src/middlewares/Auth/architecture-context.md)

---

## Testing Architecture

Tests use a Sandbox pattern. See [tests/domain-helpers/](/tests/domain-helpers/architecture-context.md).

---

## References

- ADR-001 through ADR-007.
