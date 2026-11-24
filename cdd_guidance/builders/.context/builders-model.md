# cdd_guidance/builders

A *Builder* is guidance for building a new part of CDD; *CreateAgentToolset* and *CreatePracticeGuidance* are the two builders.

- **Purpose:** Start every new toolset and practice from the same templates, so it installs and runs with the existing actions on its first try.
- **Seam (terms):** Builder, CreateAgentToolset, CreatePracticeGuidance
- **Dependencies (one-way):** harness/agent_tools, harness/guidance

## Builder : PracticeGuidance

Guidance for building a new part of CDD, such as a toolset or a practice; it works from the repository's root rather than a practice folder.

------
+ default_workspace_folder: str
----

## CreateAgentToolset : Builder

Scaffold a new agent toolset: an @agent_toolset class with @agent_tool and @agent_instructions operations.

------
----

## CreatePracticeGuidance : Builder

Scaffold a new practice: its PracticeGuidance class, its markdown, templates, and examples.

------
----
