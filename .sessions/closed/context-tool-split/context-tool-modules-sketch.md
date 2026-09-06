# context-tool-modules sketch

## Concrete kits (no I* / impl split — one test tier)

WorkspaceSession  (utilities/sessions/)
  session; read_context_index; record_context_root
  create_session; close_session

Scan  (utilities/scanners/scan.py — same kit as ScannerCollection)
  scan; _scanner_collection

PartitionPipeline  (utilities/partition_pipeline/)
  partition index segment verify_segment_completeness
  partition_guidance

Repair  (utilities/repair/)
  write_to_fix; log_fix; repair

BaseContextTool : composer + lifecycle  (context_tools/base/base_context_tool.py)
  MI merge of utilities kits + inlined lifecycle
  generate validate satisfy document
  generate_output add_generate_header
  grill sketch iterate
  generate_instructions document_instructions examples templates
  module_dir, contexts, @base_context_tool
  action prose: # Generate / Validate / Satisfy / Document in base_context_tool.md

CreateContextTool : meta generator domain  (context_tools/create_context_tool/)
  @base_context_tool domain that scaffolds new domains
  owns templates/, examples/, create_context_tool.md meta contexts

----

## Module dependencies

```
WorkspaceSession / Scan / PartitionPipeline / Repair
  (no kit→kit deps)

BaseContextTool → each utilities kit above (+ lifecycle inlined)
CreateContextTool → BaseContextTool (via @base_context_tool)
```

----

## Layout

utilities/: sessions, scanners, partition_pipeline, repair  
context_tools/base/: base_context_tool.py (+ lifecycle action md), create_context_tool/
