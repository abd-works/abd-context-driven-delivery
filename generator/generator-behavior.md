# HIERARCHY: Generator Framework

<!--
Example in code: generator.examples.car_chronicle.car_chronicle:CarChronicle (generator/examples/car_chronicle/)
Production domain: clean_code.clean_code:CleanCode
Generator spec: generator/generator_spec.py — ActionRunner expansion + direct tool calls (in-process)
Agent spec: generator/generator_agent_spec.py — agent follows instructions; assert shell tool calls
Primitives spec: primitives/primitives_spec.py — Instruction, DeclaredProperty, DeclaredOperation
Scanner spec: scanners/scanner_spec.py — Scanner, Violation, execute_scan, ScannerCollection
Per-scanner repair fixtures: clean_code/examples/<rule>/faultyAsset and repairedAsset (scanners_spec.py)
-->

Instructions

  an instruction whose value is plain prose
    the instruction is expanded
      the expanded text should remain unchanged

  an instruction whose value matches a file on disk
    the instruction is expanded
      the expanded text should include the loaded file content

  an instruction whose value matches a folder on disk
    the instruction is expanded
      the expanded text should include the loaded folder content

Action expansion

  generator_spec.py — ActionRunner.expand in-process; no subprocess

  a Clean Code generator constructed with format python
    the generate action is expanded
      action should be generate
      tools should name no tools
      instructions should inline full Concepts section from clean-code.md
      instructions should inline full examples.md
      instructions should inline full formats/python/clean-code-template.py

    the validate action is expanded
      action should be validate
      tools should name scan
      instructions should inline concepts as rubric
      instructions should inline validate.md from the generator module

    the satisfy action is expanded
      action should be satisfy
      tools should name no tools
      instructions should inline concepts and template
      instructions should inline satisfy.md from the generator module

    the repair action is expanded
      action should be repair
      tools should name scan
      instructions should inline repair.md from the generator module
      instructions should inline concepts examples and template
      instructions should substitute asset and violation arguments
      instructions should inline validate.md from the generator module
      instructions should inline generator-fix prose from repair.md

  the base Generator toolset in generator/generator.py
    the generate action is expanded
      instructions should inline meta concepts from generator.md
      instructions should inline all files from generator/templates/
      instructions should inline generate.md action prose
      instructions should inline worked samples from generator/examples

  a domain Generator whose generate_output target calls self.add_epic()
    generator/examples/car_chronicle/chronicle_with_output.py — ChronicleWithOutput
    the generate action is expanded
      tools should name add_epic
      instructions should include prose from the generate_output target

  a domain Generator with no generate_output target wired
    generator/examples/car_chronicle/car_chronicle.py — base CarChronicle
    the generate action is expanded
      instructions should not include generate-output steps from a subclass target

Scanner tools

  clean_code_spec.py — scan() on CleanCode; rules align with concept slugs in clean-code.md

  the scan tool is invoked on a Clean Code generator with format python
    the report rules should list every rule slug from formats/python/scanners/

  the scan tool is invoked with an explicit path list
    the report should be deterministic for exactly those paths

Agent

  with agent and generate action
    Agent reading this file: run in chat via @agent-spec-manifest (python -m tools agent-spec generator/generator_agent_spec.py)
    agent-instruct-read car_chronicle/car_chronicle.py, then natural generate prompt for a driving chronicle
      it should parse generate action response with instructions
      it should name no tools on generate
      ai-judge on chronicle should find first-person driving log with route and mileage

  with agent and repair action
    agent-instruct-read car_chronicle/car_chronicle.py, tools run repair with asset and violation
      it should parse repair action response with instructions
      it should name scan on repair tools list
      it should inline repair.md generator-fix and example-folder guidance
      it should substitute asset and violation arguments

Generate a Knowledge Artifact

  a Generator
    it should expose generate, validate, satisfy, and repair as actions owned by the base class
    it should expose scan as a tool on the base class

  a domain Generator with a generate_output target wired
    it should not declare its own generate action
    it should not declare its own validate action
    it should not declare its own satisfy action
    it should not declare its own repair action

Resolve Path References

  an instruction value naming a path
    it should resolve relative to that class module directory

  an instruction value with only a section heading
    the instruction is expanded
      the resolved content should come from the canonical markdown in that module directory

  an instruction value naming a subfolder with a trailing slash
    the instruction is expanded
      the resolved content should include every markdown file in that subfolder as a separate named concept

  a domain package moved to a new location with its class module
    an instruction owned by a class in that package is expanded
      the resolved content should still be correct

Produce Clean Code

  a Clean Code generator
    it should target one artifact type per class
