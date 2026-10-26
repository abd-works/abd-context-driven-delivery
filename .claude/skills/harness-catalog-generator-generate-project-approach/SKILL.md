---
name: harness-catalog-generator-generate-project-approach
description: >-
  Render ``cdd-approach.html`` for a project using mapped example artifacts.
  
  ``project_root`` is the project checkout. ``out_root`` defaults to
  ``{project_root}/catalog``. ``examples_json`` is optional JSON mapping
  practice → stage → relative path; when blank, use
  ``.context/project-approach-examples.json`` and auto-discovery.
---

Render ``cdd-approach.html`` for a project using mapped example artifacts.

``project_root`` is the project checkout. ``out_root`` defaults to
``{project_root}/catalog``. ``examples_json`` is optional JSON mapping
practice → stage → relative path; when blank, use
``.context/project-approach-examples.json`` and auto-discovery.

Use MCP tool: `catalog.generate_project_approach(project_root: 'str', out_root: 'str' = '', project_title: 'str' = '', repo_url: 'str' = '', examples_json: 'str' = '')`
