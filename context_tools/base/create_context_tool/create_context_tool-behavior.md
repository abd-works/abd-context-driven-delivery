# HIERARCHY: BaseContextTool / CreateContextTool

<!--
Example in code: context_tools.base.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle (context_tools/base/create_context_tool/examples/car_chronicle/)
Production domain: context_tools.clean_engineering.clean_engineering:CleanEngineering
Context spec: context_tools/base/base_context_tool_spec.py — ActionRunner expansion + direct tool calls (in-process)
Agent spec: context_tools/base/create_context_tool_agent_spec.py — agent follows instructions; assert shell tool calls
Primitives specs: primitives/instructions/instruction_spec.py, primitives/declared/declared_spec.py, primitives/assets/asset_spec.py, primitives/assets/markdown_extractor_spec.py
Scanner spec: context_tools/scanners/scanner_spec.py — Scanner, Violation, execute_scan, ScannerCollection
Per-scanner repair fixtures: context_tools/clean_engineering/evals/engineering/<rule>/faultyAsset and repairedAsset (scanners_spec.py)
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
      instructions should inline Concepts from clean_engineering (§ Contexts in clean_engineering.md)
      instructions should inline full examples.md
      instructions should inline templates under context_tools/clean_engineering/templates/

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

  the base BaseContextTool toolset in context_tools/base/context_tool.py
    the generate action is expanded
      instructions should inline meta contexts from context_tool.md
      instructions should inline all files from context_tools/base/templates/
      instructions should inline generate.md action prose
      instructions should inline worked samples from context_tools/examples

  a domain BaseContextTool whose generate_output target calls self.add_epic()
    context_tools/base/create_context_tool/examples/car_chronicle/chronicle_with_output.py — ChronicleWithOutput
    the generate action is expanded
      tools should name add_epic
      instructions should include prose from the generate_output target

  a domain BaseContextTool with no generate_output target wired
    context_tools/base/create_context_tool/examples/car_chronicle/car_chronicle.py — base CarChronicle
    the generate action is expanded
      instructions should not include generate-output steps from a subclass target

Scanner tools

  context_tools/clean_engineering/scanners/scanners_spec.py — scan rules under evals/engineering/

  the scan tool is invoked on a CleanEngineering generator with format python
    the report rules should list every rule slug from context_tools/clean_engineering/scanners/

  the scan tool is invoked with an explicit path list
    the report should be deterministic for exactly those paths

Agent

  with agent and generate action
    Agent reading this file: run in chat via @agent-spec-manifest (python -m tools agent-spec context_tools/base/create_context_tool_agent_spec.py)
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

  a BaseContextTool
    it should expose generate, validate, satisfy, repair, partition, index, and segment as actions owned by the base class
    it should expose scan as a tool on the base class

  a CarChronicle (or any domain Context) expanding partition
    the partition action is expanded
      instructions should inline partition.md action prose from partition_pipeline
      instructions should inline contexts
      instructions should inline partition guidance (domain partition.md or default)
      instructions should nest index and segment prose

  a domain BaseContextTool with partition.md
    the index action is expanded
      instructions should inline that context's partition.md guidance
      instructions should name the index file as {subject}-index.md (corpus basename, not toolset)

  a domain BaseContextTool without partition.md
    the index action is expanded
      instructions should inline the default partition guidance prose

  a domain BaseContextTool with a generate_output target wired
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
