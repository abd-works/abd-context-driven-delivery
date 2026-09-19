Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity builds on these behaviours, so the story map must describe operations that named actors perform and results they can observe.

story_map — ** Define a visual hierarchy of how users and systems achieve business outcomes: `Epic` -> nestable `Sub-Epic` -> `Story`. It is easier to change the map while Stories are titles than after Scenarios, screens, and tests exist.

Use MCP tool: `stories.fidelityInstructions(fidelity: 'story_map')`

scenarios — ** Refine Stories into concrete examples with preconditions, triggering operations, and observable outcomes. A Scenario defines both the required behaviour and the evidence that will show whether it works.

Use MCP tool: `stories.fidelityInstructions(fidelity: 'scenarios')`

acceptance_tests — ** Turn agreed Scenarios into executable evidence and working production behavior. For greenfield work, begin with a failing test that calls the intended production interface. For brownfield capture, first preserve observed behaviour and mark intended changes explicitly.

Use MCP tool: `stories.fidelityInstructions(fidelity: 'acceptance_tests')`
