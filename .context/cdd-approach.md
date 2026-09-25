# Context Driven Delivery: Enabling clients to clean, clarify, and transform context into working solutions

- **Context**
  - Systems
  - Dialogue 
  - Documentation
  - Architecture

Collect every source that describes the problem to be solved, the current conditions, constraints, and the intended solution.  Business, Customer, Technology

Parse code, instrument systems, orchestrate running tests,  documentation, and the conversation with experts. 

Extract, parse, categorize, index for easier ai consumption

- **Discovery**
  - Outcome
  - Journey
  - Architecture

Refine context into lower fidelity artifacts that make it easier to align on the overarching solution, catch systemic errors, and avoide failure  cascasding downstream.

Focus on how outcome translate to user journeys,and map those use journey to system behavior

Define enough structure to establish how domaion boundaries and technology modules connect to each

- **Specification**
  - Increment
  - Experience
  - Prototype

Ceate machine executable specifucations; one small slice of the journey at a time.

Refine understanding of the business required to modularize domain validity access, persistence, consistency, and intrgration

Write example driven scenario backed by domain driven operations 

Define / extend rules, templates and transformers that aid ai in generating toward the target tech stack

Generate working UI prototypes that pass all tests.

**Implement**
  - Tests
  - Touchpoint
  - Solution

Build each slice onto the target stack. AI oversees deterministic tools so that the same input produces results that are gaurdrailed by safety and quaility standards.

Automate scenario specifications to cover user, system, and module connecting interfaces

Eval every error, both technical and functional to improve the ai delivery system. Feed results into AI's every growing knowledge repository


- **Validate**
  - Value
  - Economics
  - Feasibility
  - Learning

Confirm user impact; dpoes the intended value and observed behave line up.

Confirm the economics, revenue, growth, savings, or profit match the investment

Confirm the solution is feasible. Are costs, risk, and operations meetinh expectation.

Inject all feedback back into the context, so Ai benefts from compunded leanring over time


## Principles of CDD
**Iterate and Learn** — Layer context and limit AI runs to the cognitive load of what humans can absorb; guide, validate, and improve the system.  

[Sketch](https://github.com/abd-works/abd-context-driven-delivery/blob/main/actions/sketch/sketch.md) - A tool that engage a person and AI in an interactive probe, grill, illustrate, and align session. Multiple rounds are used to scaffold stories, domain, UX, etc  in order to establish rapid understanding and feedback. 

**Code is context** — managing context is critucal, and with the right product engineering practices your code can be the primary source of truth that describes how both the business and technology work. Linking, versioning, reviews, auditing come practically for free. 

[Stories](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/stories.md) - A tool that generates working code that describes both functional and business logic.  Flipping to and from [documententaion](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/examples/telco-website/onboard-a-customer/create-customer/create-unconfirmed-user/create_unconfirmed_user_story.test.md) and  <-> [code](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/examples/telco-website/onboard-a-customer/create-customer/create-unconfirmed-user/create_unconfirmed_user_story.test.ts) is seamless.

**Mulitiple Perspectives** — Define and connect context across product, engineering, and operations, replacing scattered docs, tickets, and tribal memory with an integratred knowledge graph.

The [knowledge graph](https://github.com/abd-works/abd-context-driven-delivery/tree/main/harness/knowledge_graph) is these models and the relationships between them. CodeQL reads them out of the code.

- **Stories** — actors, systems, and the interactions that deliver the solution
- **Domain-driven design** — the business concepts and the boundaries that protect them
- **Clean engineering** — modules, contracts, and the code that can be generated and checked
- **Behavior-driven development** — behavior tests written in the language of the domain
- **User experience** — how people move through and act on the solution




