# HIERARCHY: Discoverable Toolsets

<!--
Example in code: tools.examples.car:Car
Class description: "Operate a car — start, stop, and read current state."
Tools: start, stop, drive, accelerate, decelerate, speak. Resources: make, model, year, personality, running.
Agent: agent-instruct runs cursor-agent (cli harness) or chat subagents when the spec declares harness: in_chat via @agent-spec-manifest; the second instruct parses fenced tools run yaml into ai-response (ok, result, resources). Runbook: python -m tools agent-spec <spec.py>.
Action specs: action/agents_spec.py and action/agents_agent_spec.py use action.examples.car:Car
-->

a class
  with a toolset applied
    with a class-level description
      it should expose instructions matching the class-level description
    with methods marked as tools and method-level descriptions
      the toolset manifest
        it should provide a manifest for the whole toolset
        it should contain a tool manifest for every marked method
        it should include toolset-level instructions matching the class-level description
      every marked method
        the tool manifest
          it should match the entry contained in the toolset manifest
          it should carry instructions matching the method description
          it should carry a machine-readable typed signature for parameters and return values
        it should be invokable through a standardized command-line interface
    with properties marked as resources and property-level descriptions
      the toolset manifest
        it should include a resource entry for every marked property
        it should carry a machine-readable typed signature for retrieving the current values of all marked properties
    with agent()
      agent-instruct("read tools/examples/car.py from the workspace")
      agent-instruct("create a car based on the general lee from the Dukes of Hazzard")
        it should parse the fenced CLI yaml into ai-response
        ai-response.make should contain Dodge
        ai-response.model should contain Charger
        ai-response.year should be 1969
        ai-judge on ai-response.personality should find a rebellious, high-spirited, and loyal country boy

## Example in code

a Car
  with a toolset applied

  with a make, model, and personality supplied at creation
    the make resource
      it should carry the supplied manufacturer
