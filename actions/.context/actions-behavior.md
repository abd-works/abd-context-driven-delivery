# HIERARCHY: Agent Actions

<!--
Example in code: actions.examples.car:Car
Action: travelTo — orchestrates start, accelerate, decelerate, stop, speak
Non-agentic spec: actions/actions_spec.py
Agentic spec: actions/actions_agent_spec.py
-->

a class
  with a toolset that declares @action recipes
    the travelTo action
      it should appear in the manifest with kind action and referenced tools
      it should expand into instructions when invoked through the command-line interface
    with agent and travelTo action
      Agent reading this file: run in chat via @agent-spec-manifest (python -m tools agent-spec actions/actions_agent_spec.py)
      create General Lee, invoke travelTo, follow instructions
        it should parse travelTo action response with instructions
        it should invoke at least start and speak tools while following instructions
        ai-judge on the story should find an entertaining General Lee adventure
