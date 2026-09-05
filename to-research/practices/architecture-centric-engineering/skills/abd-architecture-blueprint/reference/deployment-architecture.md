# Deployment Architecture Diagram

## What it is

A diagram showing where each platform component runs: the environments (Production, Staging, Preview), the infrastructure nodes (cloud region, VPC, AZ, managed service, cluster), the infrastructure services (load balancer, CDN, API gateway, WAF), and the container or process instances that run inside them — including the OS image for each when more than one is in use. Based on C4 Deployment (Level 4).

## What it is for

- Answer "where does each part of the system actually run?" before any code is written or reviewed.
- Surface infrastructure decisions (cloud provider, region, managed vs self-hosted services) that drive cost, compliance, and availability planning.
- Make the redundancy model (multi-AZ, single-region, active-active) explicit rather than assumed.
- Give the blueprint's mechanism descriptions a physical environment to refer to (e.g. "both ECS tasks share the same Redis cluster," "secrets injected by the PaaS at deploy time").
- Give operations teams a reference for incident response — what nodes exist, how traffic flows, where to look when something fails.

## Questions it answers

- In which cloud region and availability zone does each component run?
- What managed services (RDS, Atlas, ElastiCache, SQS, etc.) are in use?
- What does the network path from a browser request to the data store look like in production?
- What environments exist, and how do they differ from production?
- When more than one OS image is in use, which process uses which and why?

## What it does NOT answer

- What technology stack or framework each component uses (→ Platform Architecture diagram).
- What is inside any service at the code level (→ Components section of the blueprint, Architecture Reference).
- Why the deployment model was chosen (→ ADRs in the outline or blueprint).

## Notation

Environments are outer rounded boxes. Infrastructure nodes (region, VPC, AZ, managed service) are nested boxes inside the environment. Infrastructure services (load balancer, CDN, API gateway) use a diamond or cylinder shape. Container instances (running processes) are solid inner boxes. Arrows carry a protocol label (HTTPS, TCP wire protocol, AMQP, etc.) and whether the path crosses a public or private network boundary. Solid arrows = synchronous runtime connection; dashed arrows = async or event-driven.

## Element types

| Element type | What it represents |
|---|---|
| Deployment Environment | A named target (Production, Staging, Preview, Development) |
| Deployment Node | An infrastructure boundary that hosts other nodes — cloud region, VPC, AZ, Kubernetes cluster, managed service tier |
| Infrastructure Node | A supporting network component that processes or routes traffic — load balancer, CDN distribution, API gateway, WAF, DNS |
| Container Instance | A running application process, service, or database instance — named after the platform component it hosts |
| Connection | An arrow between nodes; label states protocol and which network boundary it crosses |

## OS images section

When more than one operating system image is in use across container instances (e.g. API containers on Alpine, GPU workers on Ubuntu, batch jobs on Amazon Linux), the deployment section of the blueprint includes an **OS images table** alongside the diagram:

| Container / process | OS / runtime image | Notes |
|---|---|---|
| {Service name} | {Image — e.g. node:20-alpine} | {Why — e.g. minimal attack surface, FIPS compliance} |
| {Worker name} | {Image} | {Notes} |

Omit this table when all containers share a single OS image.

## Relationship to other diagrams

| Other diagram | Relationship |
|---|---|
| Platform Architecture | Shows what components run and how they connect — Deployment Architecture shows where they are hosted |
| System Context | Shows actors and external systems — Deployment Architecture shows the infrastructure that hosts the systems in that diagram |
| Architecture Reference | Shows how mechanisms work in code — Deployment Architecture provides the physical infrastructure context those mechanisms operate in |
