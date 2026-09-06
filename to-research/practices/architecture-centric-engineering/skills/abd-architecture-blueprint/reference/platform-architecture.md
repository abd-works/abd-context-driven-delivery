# Platform Architecture Diagram

## What it is

A runtime view of every software component the system is composed of: client applications, backend services, background workers, data stores, CDN/edge nodes, and third-party integrations — showing what technology each runs on and how the components connect. There is no deployment topology here (which server, which region, which OS image — that is the Deployment Architecture diagram).

Based loosely on C4 Level 2 (Container diagram) but scoped to the platform runtime layer, not internal components.

## What it is for

- Show a new engineer what processes actually run when the system is deployed and how they talk to each other.
- Make explicit the technology choice for each runtime component so platform decisions are visible without reading narrative prose.
- Surface integration points (CDN-to-service, service-to-database, service-to-third-party) with their protocols.
- Give the blueprint's mechanism descriptions a physical runtime to refer to (e.g. "Redis cache cluster," "ECS Fargate tasks," "Atlas free-tier cluster").

## Questions it answers

- What processes run in this system?
- What technology (runtime, framework, version) does each process use?
- Which data store does each service connect to, and over what protocol?
- Which third-party services are wired in at the platform level and how?
- What is the request path from the browser (or API caller) to the data store?

## What it does NOT answer

- Which environment (production, staging, dev) the components run in (→ Deployment Architecture diagram).
- What OS image or infrastructure node hosts each process (→ Deployment Architecture diagram).
- What is inside any service (→ Components section of the blueprint, Architecture Reference).
- Why these technology choices were made (→ ADRs in the outline, mechanism NFR justifications).

## Notation

Each runtime process is a named, labelled box. Technology badges appear inside or below the box. Data stores use a cylinder shape. CDN/edge nodes use a diamond or rounded box at the periphery. Third-party integrations are grouped separately at the edge of the diagram. Arrows carry a protocol label (HTTPS/REST, MongoDB wire protocol, AMQP, etc.). Solid arrows = synchronous call; dashed arrows = async or event-driven.

## Element types

| Element type | What it represents |
|---|---|
| Client Application | A browser-side or mobile runtime (React SPA, mobile app, desktop client) |
| Backend Service | A server-side process handling synchronous requests (Express API, Spring Boot, Django, etc.) |
| Background Worker | A long-running process that consumes a queue, processes webhooks, or runs scheduled jobs |
| Data Store | A database, cache, or object store (PostgreSQL, MongoDB, Redis, S3, etc.) |
| CDN / Edge | A content delivery network or edge proxy that caches assets or routes traffic |
| Third-Party Integration | An external SaaS or API the platform depends on at runtime (payment gateway, identity provider, geolocation API, etc.) |
| Connection | An arrow between two elements; label states the protocol and direction of data flow |

## Relationship to other diagrams

| Other diagram | Relationship |
|---|---|
| System Context | Shows what the system does and who uses it — Platform Architecture zooms in to show what it actually runs as |
| Layered Architecture | Shows the logical layer structure — Platform Architecture shows the physical runtime component that implements those layers |
| Deployment Architecture | Shows where platform components run — Platform Architecture shows what they are and how they connect |
