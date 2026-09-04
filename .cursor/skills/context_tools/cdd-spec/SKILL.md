---
name: cdd-spec
description: "Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd."
disable-model-invocation: true
---

# cdd-spec

Use cdd guidance at `spec` fidelity only.

Use higher-level fidelity guidance only when required information is missing. Reference these commands with `@`; do not inline their content:
@cdd-discovery

Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd.
Call guidance on each stage child and pass that child to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.