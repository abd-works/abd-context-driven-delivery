# System Context Diagram

## What it is

A high-level diagram showing every software system in scope and the humans and external systems each one interacts with. There is no internal structure — each system is a single box. The diagram is technology-agnostic and readable by non-technical stakeholders.

Based on C4 Level 1 (System Context). Most solutions are **multi-system**: the diagram shows System A, System B, System C alongside each other, with actors and external services around them. It is not limited to "the system" plus its externals.

## What it is for

- Fix the boundary of what is in scope and what is outside it before any design work begins.
- Make explicit every human role and every external system the solution touches.
- Give stakeholders a picture they can read without understanding technology.
- Surface integration points that will drive ADR decisions.

## Questions it answers

- What software systems make up this solution?
- Who are the human actors and what system do they interact with?
- What external systems (SaaS, partner APIs, legacy platforms, other internal systems) are connected and which of our systems do they connect to?
- What crosses the boundary of the solution?
- What does each system's relationship with the outside world look like at a glance?

## Notation

Each software system is a single named box. Human actors are shown as person icons. External systems are boxes at the periphery. Arrows are labelled with an active verb phrase describing the interaction. No technology details, no database symbols, no API paths.

## Element types

| Element type | What it represents |
|---|---|
| Software System (in scope) | A system the team owns and is responsible for — shown prominently, typically one or more boxes |
| Person | A named human role that interacts directly with one or more of the systems in scope |
| External Software System | Any system outside the solution boundary — SaaS providers, partner APIs, other teams' systems, legacy platforms |
| Relationship | A directed arrow between any two elements; labelled with what crosses the boundary and why |

## Scope note

A single-system solution has one in-scope box at the centre. A multi-system solution (microservices suite, platform + admin console + mobile backend, etc.) has several in-scope boxes — each is a peer on the diagram, not a sub-element. Actors and external services connect to whichever in-scope system they actually interact with.
