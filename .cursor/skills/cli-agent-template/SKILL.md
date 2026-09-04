---
name: cli-agent-template
description: "Create, list, and apply reusable job templates for /cli-agent."
disable-model-invocation: true
---

Create, list, and apply reusable job templates for /cli-agent.

A template is a named list of jobs — same shape as a job queue entry:
``prompt``, ``tools`` (optional), ``actions`` (optional), ``judge`` (optional).
Templates live in ``job-templates/`` by default; pass ``path`` for a project-specific location.

## Create a template

Call this tool with ``name``, ``jobs``, and an optional ``description``.

## List templates

Call `list_templates()` to see all saved names. Pass ``path`` for a project folder.

## Apply a template

Call `use_template(name)` to enqueue its jobs on the active session, then run `/cli-agent`.
Pass ``overrides`` (dict) to merge changes into every job first — e.g. swap a prompt or enable a judge.

## Match to a request

If the user's request sounds like an existing template, call `list_templates()` and offer
the closest match via AskQuestion before building a queue from scratch.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: cli_agent.cli_agent:CliAgent
tool: add_template
```
.\tools.ps1 run -
