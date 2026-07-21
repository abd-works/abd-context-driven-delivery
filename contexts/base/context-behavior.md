# HIERARCHY: Context Framework

<!--
Example in code: contexts.base.examples.car_chronicle.car_chronicle:CarChronicle (contexts/base/examples/car_chronicle/)
Production domain: contexts.clean_engineering.clean_engineering:CleanEngineering
Context spec: contexts/base/context_spec.py — ActionRunner expansion + direct tool calls (in-process)
Agent spec: contexts/base/context_agent_spec.py — agent follows instructions; assert shell tool calls
Primitives specs: primitives/instructions/instruction_spec.py, primitives/declared/declared_spec.py, primitives/assets/asset_spec.py, primitives/assets/markdown_extractor_spec.py
Scanner spec: contexts/scanners/scanner_spec.py — Scanner, Violation, execute_scan, ScannerCollection
Per-scanner repair fixtures: contexts/clean_engineering/evals/engineering/<rule>/faultyAsset and repairedAsset (scanners_spec.py)
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

  context_spec.py — ActionRunner.expand in-process; no subprocess

  a CleanEngineering generator constructed with format python
    the generate action is expanded
      action should be generate
      tools should name no tools
      instructions should inline Concepts from clean_engineering (contexts.md / § Contexts)
      instructions should inline full examples.md
      instructions should inline templates under contexts/clean_engineering/templates/

    the validate action is expanded
      action should be validate
      tools should name scan
      instructions should inline contexts as rubric
      instructions should inline validate.md from the contexts module

    the satisfy action is expanded
      action should be satisfy
      tools should name no tools
      instructions should inline contexts and template
      instructions should inline satisfy.md from the contexts module

    the repair action is expanded
      action should be repair
      tools should name scan
      instructions should inline repair.md from the contexts module
      instructions should inline contexts examples and template
      instructions should substitute asset and violation arguments
      instructions should inline validate.md from the contexts module
      instructions should inline generator-fix prose from repair.md

  the base Context toolset in contexts/base/context.py
    the generate action is expanded
      instructions should inline meta contexts from context.md
      instructions should inline all files from contexts/base/templates/
      instructions should inline generate.md action prose
      instructions should inline worked samples from contexts/examples

  a domain Context whose generate_output target calls self.add_epic()
    contexts/base/examples/car_chronicle/chronicle_with_output.py — ChronicleWithOutput
    the generate action is expanded
      tools should name add_epic
      instructions should include prose from the generate_output target

  a domain Context with no generate_output target wired
    contexts/base/examples/car_chronicle/car_chronicle.py — base CarChronicle
    the generate action is expanded
      instructions should not include generate-output steps from a subclass target

Scanner tools

  contexts/clean_engineering/scanners/scanners_spec.py — scan rules under evals/engineering/

  the scan tool is invoked on a CleanEngineering generator with format python
    the report rules should list every rule slug from contexts/clean_engineering/scanners/

  the scan tool is invoked with an explicit path list
    the report should be deterministic for exactly those paths

Agent

  with agent and generate action
    Agent reading this file: run in chat via @agent-spec-manifest (python -m tools agent-spec contexts/base/context_agent_spec.py)
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

  a Context
    it should expose generate, validate, satisfy, repair, partition, index, and segment as actions owned by the base class
    it should expose scan as a tool on the base class

  a CarChronicle (or any domain Context) expanding partition
    the partition action is expanded
      instructions should inline partition.md action prose from base-context
      instructions should inline contexts
      instructions should inline partition guidance (domain partition.md or default)
      instructions should nest index and segment prose

  a domain Context with partition.md
    the index action is expanded
      instructions should inline that context's partition.md guidance
      instructions should name the index file as {toolset_name}-index.md

  a domain Context without partition.md
    the index action is expanded
      instructions should inline the default partition guidance prose

  a domain Context with a generate_output target wired
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
