---
name: cdd-spec
description: "Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd."
disable-model-invocation: true
---

# cdd-spec

Use cdd guidance at `spec` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@cdd-discovery

Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd.
Call guidance on each stage child and pass that child to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.