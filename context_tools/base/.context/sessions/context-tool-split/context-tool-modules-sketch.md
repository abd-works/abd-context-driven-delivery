# context-tool-modules sketch

## Concrete kits (no I* / impl split — one test tier)

WorkspaceSession  (utilities/workspace_session/)
  session; read_context_index; record_context_root
  create_session; close_session

Scan  (utilities/scanners/scan.py — same kit as ScannerCollection)
  scan; _scanner_collection

PartitionPipeline  (utilities/partition_pipeline/)
  partition index segment verify_segment_completeness
  partition_guidance

Repair  (utilities/repair/)
  write_to_fix; log_fix; repair

ArtifactLifecycle  (context_tools/base/artifact_lifecycle/ — CT-only)
  generate validate satisfy document
  generate_output add_generate_header
  grill sketch iterate
  generate_instructions document_instructions examples templates
  -> utilities GrillContext Sketcher Iterator (decorators)

ContextTool : composer  (context_tools/base/context_tool.py)
  MI merge of kits + shared domain face (module_dir, contexts) + @context_tool
  hosts base-context/
  Concept-owned instruction slots live on kits (partition_guidance, generate/document/examples/templates, …)

----

## Module dependencies

```
WorkspaceSession / Scan / PartitionPipeline / Repair / ArtifactLifecycle
  (no kit→kit deps)

ContextTool → each kit above
```

----

## Layout

utilities/: workspace_session, scanners, partition_pipeline, repair  
context_tools/base/: artifact_lifecycle, context_tool.py, base-context/
