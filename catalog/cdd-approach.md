# Approach

The CDD harness helps you guide AI to refine unstructured context in stages until it lives as working code.

## Stages

### Context

id: context
shape: square
scope_name: Context
scope_width: square
items: Business Model | User Traction | Operating Benchmarks

Collect every source that describes the problem to be solved, the current conditions, constraints, and the intended solution — business, customer, and technology.

Extract documentation. Interview experts.

Parse code, instrument systems, and orchestrate running tests. Categorize and index the material so AI can consume it cleanly.

### Discovery

id: discovery
board_key: discovery
shape: solution
scope_name: Whole solution
scope_width: wide / shallow
items: Outcome | Experience | Architecture

Refine context into lower-fidelity artifacts that make it easier to align on the overarching solution, catch systemic errors, and avoid failure cascading downstream.

Focus on how outcomes translate to user journeys, and map those journeys to system behavior.

Define enough structure to establish how domain boundaries and technology modules connect.

### Specification

id: specification
board_key: spec
shape: sprint
scope_name: Sprint
scope_width: narrow / deeper
items: Increment | Prototype | Reference

Create machine-executable specifications — one small slice of the journey at a time.

Refine the business understanding needed to modularize domain validity, access, persistence, consistency, and integration.

Write example-driven scenarios backed by domain-driven operations, and generate working UI prototypes that pass their tests.

### Implement

id: implementation
board_key: engineer
shape: story
scope_name: Story
scope_width: narrowest / deep
items: Tests | Interface | Solution

Build each slice onto the target stack. AI oversees deterministic tools so the same input produces results guarded by safety and quality standards.

Automate scenario specifications to cover user, system, and module-connecting interfaces.

Evaluate every error — technical and functional — and feed results back into the growing knowledge repository.

### Validate

id: validate
shape: story
scope_name: Story
scope_width: narrowest / deep
items: Economics | Impact | Feasibility

Confirm the economics: revenue, growth, savings, or profit against the investment.

Confirm user impact — does the intended value line up with the behavior that was observed?

Confirm feasibility for cost, risk, and operations, then inject that feedback back into the context so AI compounds learning over time.

## Context Driven Delivery Practices

### Iterate and Learn

slug: iterate-and-learn
kind: windows

- Limit each AI run to the cognitive load of the team, so people can guide, review, and adjust what it generates.
- Keep the context window small. Even frontier models produce better output well under their maximum.
- Layer context through successive generations. Each pass increases fidelity.

The CDD harness includes [Sketch](https://github.com/abd-works/abd-context-driven-delivery/blob/main/actions/sketch/sketch.md), a session where a person and AI probe, grill, illustrate, and align. Multiple rounds scaffold stories, domain, UX, and more for rapid understanding and feedback.

### Product Engineering

slug: product-engineering
kind: descriptions

- The fundamentals of product engineering have not changed.
- Ground AI delivery in test-driven, iterative practices that easily connect business outcomes, user impact, and system behavior to technology implementation.

### Context Storming

slug: context-storming
kind: storm

- Define and connect context across product, engineering, and operations. Bring those artifacts into one knowledge graph, in place of scattered docs, tickets, and tribal memory.
- Collaboratively build artifacts at the right level of abstraction to support the right level of decision making.

The CDD harness includes the [knowledge graph](https://github.com/abd-works/abd-context-driven-delivery/tree/main/harness/knowledge_graph), the models and the relationships between them. CodeQL reads them out of the code.

### Code Is Context

slug: code-is-context
kind: spec

- Code is the source of truth for how the business and the technology work. Linking, versioning, reviews, and auditing come with it.
- Refine context into an executable specification that tests the actual solution.
- Write the code as a direct expression of the design, so it can be turned into docs and back.

The CDD harness includes [Stories](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/stories.md), a practice that generates working code for both functional and business logic. Flipping between [documentation](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/examples/telco-website/onboard-a-customer/create-customer/create-unconfirmed-user/create_unconfirmed_user_story.test.md) and [code](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/examples/telco-website/onboard-a-customer/create-customer/create-unconfirmed-user/create_unconfirmed_user_story.test.ts) is seamless.

## Library

Our CDD harness is a library of skills, agents and tools that bring the best of agile product, delivery, and engineering practices into the age of AI.
