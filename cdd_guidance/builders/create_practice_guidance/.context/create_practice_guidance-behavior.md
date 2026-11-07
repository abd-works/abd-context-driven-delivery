# HIERARCHY: CreatePracticeGuidance

<!--
Production builder: cdd_guidance.builders.create_practice_guidance.create_practice_guidance:CreatePracticeGuidance
Builder spec: cdd_guidance/builders/create_practice_guidance/create_practice_guidance_spec.py
Templates the builder hands the agent: cdd_guidance/builders/create_practice_guidance/templates/ (domain-md.md, domain-toolset.py, domain-examples.md)
Model the builder copies: cdd_guidance/practices/stories/stories.py (a practice's thin .py) and stories.md
PracticeGuidance behavior (how any practice assembles its overview, guidance, rules, fidelities, templates, and examples, and how the shared actions run on it): harness/guidance/guidance_spec.py, harness/guidance/practice_guidance_behavior_spec.py, and the behavior section of harness/guidance/.context/practice-guidance-sketch.md
-->

CreatePracticeGuidance is the PracticeGuidance a person runs to add a new practice under `cdd_guidance/practices/`. It
owns no actions of its own: Generate, Validate, Satisfy, and Repair are the shared actions run on it, so this outline
covers only what the builder adds.

CreatePracticeGuidance meta generator

  that has been created
    it should key the index from the install folder name
    it should default the workspace folder to the repo root
    it should resolve module_dir to the create_practice_guidance package
    it should not expose generate, validate, satisfy, or repair on Guidance

  guidance expands meta face
    it should inline practice guidance from create_practice_guidance.md
