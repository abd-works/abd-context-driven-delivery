# Facts each node holds, by practice and node type (2026-11-22)

Read from the saved knowledge graph of this repository, `.context/graph.json`, saved 2026-11-21. It holds three practices: Clean Engineering, Stories and DDD. BDD and UX were not loaded into it, so their nodes are not listed. Every node also has a name, a type, a practice, a file, a first and last line, and a stage; those are not repeated below. The count after each fact is the number of nodes of that type that record it. None of these facts is shown in the graph tree of the Files app, which shows a node's name, type, edges and rules.

## Clean Engineering

### Parameter — 14060 nodes

| Fact | Nodes that record it |
|---|---|
| `type_hint` | 14060 |
| `operation_name` | 14060 |
| `property_setter` | 14060 |
| `in_typed_language` | 14060 |

### Operation — 11696 nodes

| Fact | Nodes that record it |
|---|---|
| `line_count` | 11696 |
| `max_control_flow_depth` | 11696 |
| `has_bare_catch` | 11696 |
| `swallows_exceptions` | 11696 |
| `unnamed_literal_numbers` | 11696 |
| `is_static` | 11696 |
| `is_private` | 11696 |
| `is_classmethod` | 11696 |
| `is_property` | 11696 |
| `is_setter` | 11696 |
| `published_as_tool` | 11696 |
| `body_fingerprint` | 11696 |
| `callees` | 11696 |
| `peer_private_access` | 11696 |
| `io_and_domain` | 11696 |
| `io_and_domain_callees` | 11696 |
| `raises_on_empty` | 11696 |
| `exception_without_message` | 11696 |
| `generic_exception_message` | 11696 |
| `mutates_without_record` | 11696 |
| `prose_comment` | 11696 |
| `bold_interaction_lines` | 11696 |
| `bold_invariant_lines` | 11696 |
| `owner` | 11696 |
| `packed_parameters` | 11696 |
| `return_type` | 11696 |
| `value_type` | 11696 |
| `body_text` | 11696 |
| `exempt_relationships` | 2561 |
| `duplicate_of` | 9 |
| `near_copy_of` | 4 |
| `exception_gives_own_message` | 4 |

### Property — 5463 nodes

| Fact | Nodes that record it |
|---|---|
| `owner` | 5463 |
| `value_type` | 5463 |
| `exempt_relationships` | 5298 |
| `line_count` | 1953 |
| `max_control_flow_depth` | 1953 |
| `has_bare_catch` | 1953 |
| `swallows_exceptions` | 1953 |
| `unnamed_literal_numbers` | 1953 |
| `is_static` | 1953 |
| `is_private` | 1953 |
| `is_classmethod` | 1953 |
| `is_property` | 1953 |
| `is_setter` | 1953 |
| `published_as_tool` | 1953 |
| `body_fingerprint` | 1953 |
| `callees` | 1953 |
| `peer_private_access` | 1953 |
| `io_and_domain` | 1953 |
| `io_and_domain_callees` | 1953 |
| `raises_on_empty` | 1953 |
| `exception_without_message` | 1953 |
| `generic_exception_message` | 1953 |
| `mutates_without_record` | 1953 |
| `prose_comment` | 1953 |
| `bold_interaction_lines` | 1953 |
| `bold_invariant_lines` | 1953 |
| `packed_parameters` | 1953 |
| `return_type` | 1953 |
| `body_text` | 1953 |

### OoadClass — 2988 nodes

| Fact | Nodes that record it |
|---|---|
| `bases` | 2988 |
| `stereotypes` | 2988 |
| `method_count` | 2988 |
| `operation_shapes` | 2988 |
| `property_names` | 2988 |
| `held_fields` | 2988 |
| `constructs` | 2988 |
| `composes_peers` | 2988 |
| `peer_names` | 2988 |
| `module_helpers` | 2988 |
| `prose_comment` | 2988 |
| `prototype_swap` | 2988 |
| `bold_interaction_lines` | 2988 |
| `bold_invariant_lines` | 2988 |
| `described_by_model_document` | 355 |
| `holds_production_code` | 355 |
| `copied_fields` | 20 |
| `constructs_collaborator` | 4 |
| `data_bags_taken` | 3 |
| `copied_references` | 1 |

### Package — 205 nodes

| Fact | Nodes that record it |
|---|---|
| `has_module_context` | 205 |
| `has_bounded_context` | 205 |
| `modules_heading` | 205 |
| `names_seam` | 205 |
| `names_constraint` | 205 |
| `model_blocks` | 205 |
| `is_a_in_context` | 205 |
| `child_parent_in_context` | 205 |
| `public_source_internal` | 205 |
| `public_source_files` | 205 |
| `dependencies` | 205 |
| `imported_classes` | 205 |
| `holds_production_code` | 205 |
| `import_cycles` | 205 |
| `file_import_cycles` | 205 |
| `forwards_to_module` | 205 |
| `imported_classes_by_file` | 119 |
| `sibling_imports` | 119 |
| `exempt_relationships` | 87 |

### Module — 44 nodes

| Fact | Nodes that record it |
|---|---|
| `has_module_context` | 44 |
| `has_bounded_context` | 44 |
| `modules_heading` | 44 |
| `names_seam` | 44 |
| `names_constraint` | 44 |
| `model_blocks` | 44 |
| `is_a_in_context` | 44 |
| `child_parent_in_context` | 44 |
| `public_source_internal` | 44 |
| `public_source_files` | 44 |
| `dependencies` | 44 |
| `imported_classes` | 44 |
| `holds_production_code` | 44 |
| `import_cycles` | 44 |
| `file_import_cycles` | 44 |
| `sibling_modules_imported` | 44 |
| `subtree_class_count` | 44 |
| `public_classes` | 44 |
| `public_class_count` | 44 |
| `private_class_count` | 44 |
| `operations_total` | 44 |
| `operations_public` | 44 |
| `operations_private` | 44 |
| `seam_operations` | 44 |
| `forwards_to_module` | 44 |
| `imported_classes_by_file` | 37 |
| `sibling_imports` | 37 |
| `exempt_relationships` | 7 |

## Stories

### Then — 1822 nodes

| Fact | Nodes that record it |
|---|---|
| `keyword` | 1822 |
| `text` | 1822 |
| `phase` | 1822 |
| `concepts` | 1822 |
| `values` | 1822 |
| `linked_terms` | 1822 |
| `actor` | 1822 |
| `continuation` | 1822 |
| `callees` | 1822 |
| `body_text` | 1822 |
| `calls_reach` | 1822 |
| `model_written` | 1007 |

### Given — 1193 nodes

| Fact | Nodes that record it |
|---|---|
| `keyword` | 1193 |
| `text` | 1193 |
| `phase` | 1193 |
| `concepts` | 1193 |
| `values` | 1193 |
| `linked_terms` | 1193 |
| `actor` | 1193 |
| `continuation` | 1193 |
| `callees` | 1193 |
| `body_text` | 1193 |
| `calls_reach` | 1193 |

### Scenario — 1092 nodes

| Fact | Nodes that record it |
|---|---|
| `opening_token` | 1092 |
| `opening_class` | 1092 |
| `child_count` | 1092 |
| `child_label` | 1092 |
| `child_band` | 1092 |
| `child_target` | 1092 |
| `near_duplicate` | 1092 |
| `generic_handler` | 1092 |
| `shared_verb` | 1092 |
| `one_time_task` | 1092 |
| `artifact_name` | 1092 |
| `camel_case_path` | 1092 |
| `evidence` | 1092 |
| `is_outline` | 1092 |
| `export_names` | 993 |
| `domain_class_names` | 993 |
| `imported_modules` | 993 |

### When — 1063 nodes

| Fact | Nodes that record it |
|---|---|
| `keyword` | 1063 |
| `text` | 1063 |
| `phase` | 1063 |
| `concepts` | 1063 |
| `values` | 1063 |
| `linked_terms` | 1063 |
| `actor` | 1063 |
| `continuation` | 1063 |
| `callees` | 1063 |
| `body_text` | 1063 |
| `calls_reach` | 1063 |

### Story — 563 nodes

| Fact | Nodes that record it |
|---|---|
| `opening_token` | 563 |
| `opening_class` | 563 |
| `child_count` | 563 |
| `child_label` | 563 |
| `child_band` | 563 |
| `child_target` | 563 |
| `near_duplicate` | 563 |
| `generic_handler` | 563 |
| `shared_verb` | 563 |
| `one_time_task` | 563 |
| `artifact_name` | 563 |
| `camel_case_path` | 563 |
| `evidence` | 563 |
| `scenario_count` | 563 |
| `export_names` | 563 |
| `domain_class_names` | 563 |
| `imported_modules` | 563 |
| `not_on_story_map` | 31 |

### Example — 226 nodes

| Fact | Nodes that record it |
|---|---|
| `opening_token` | 226 |
| `opening_class` | 226 |
| `child_count` | 226 |
| `child_label` | 226 |
| `child_band` | 226 |
| `child_target` | 226 |
| `near_duplicate` | 226 |
| `generic_handler` | 226 |
| `shared_verb` | 226 |
| `one_time_task` | 226 |
| `artifact_name` | 226 |
| `camel_case_path` | 226 |
| `evidence` | 226 |
| `source_names` | 226 |
| `source_reads` | 226 |
| `exempt_relationships` | 32 |
| `export_names` | 20 |

### SubEpic — 95 nodes

| Fact | Nodes that record it |
|---|---|
| `opening_token` | 95 |
| `opening_class` | 95 |
| `child_count` | 95 |
| `child_label` | 95 |
| `child_band` | 95 |
| `child_target` | 95 |
| `near_duplicate` | 95 |
| `generic_handler` | 95 |
| `shared_verb` | 95 |
| `one_time_task` | 95 |
| `artifact_name` | 95 |
| `camel_case_path` | 95 |
| `evidence` | 95 |

### Epic — 13 nodes

| Fact | Nodes that record it |
|---|---|
| `opening_token` | 13 |
| `opening_class` | 13 |
| `child_count` | 13 |
| `child_label` | 13 |
| `child_band` | 13 |
| `child_target` | 13 |
| `near_duplicate` | 13 |
| `generic_handler` | 13 |
| `shared_verb` | 13 |
| `one_time_task` | 13 |
| `artifact_name` | 13 |
| `camel_case_path` | 13 |
| `evidence` | 13 |

## DDD

### ValueObject — 17 nodes

| Fact | Nodes that record it |
|---|---|
| `bases` | 17 |
| `stereotypes` | 17 |
| `method_count` | 17 |
| `operation_shapes` | 17 |
| `property_names` | 17 |
| `held_fields` | 17 |
| `constructs` | 17 |
| `composes_peers` | 17 |
| `peer_names` | 17 |
| `module_helpers` | 17 |
| `prose_comment` | 17 |
| `prototype_swap` | 17 |
| `bold_interaction_lines` | 17 |
| `bold_invariant_lines` | 17 |
| `peer_private_operations` | 17 |
| `public_derive_operations` | 17 |
| `delegating_operations` | 17 |
| `identity_free_loads` | 17 |
| `named_for_its_kind` | 17 |
| `public_operation_names` | 17 |
| `lifecycle_operations` | 17 |
| `drives_a_screen` | 17 |
| `copied_fields` | 1 |

### Aggregate — 3 nodes

| Fact | Nodes that record it |
|---|---|
| `has_module_context` | 3 |
| `has_bounded_context` | 3 |
| `modules_heading` | 3 |
| `names_seam` | 3 |
| `names_constraint` | 3 |
| `model_blocks` | 3 |
| `is_a_in_context` | 3 |
| `child_parent_in_context` | 3 |
| `dependencies` | 3 |
| `imported_classes` | 3 |
| `bare_classes` | 3 |

### EntityRoot — 2 nodes

| Fact | Nodes that record it |
|---|---|
| `bases` | 2 |
| `stereotypes` | 2 |
| `method_count` | 2 |
| `operation_shapes` | 2 |
| `property_names` | 2 |
| `held_fields` | 2 |
| `constructs` | 2 |
| `composes_peers` | 2 |
| `peer_names` | 2 |
| `module_helpers` | 2 |
| `prose_comment` | 2 |
| `prototype_swap` | 2 |
| `bold_interaction_lines` | 2 |
| `bold_invariant_lines` | 2 |
| `peer_private_operations` | 2 |
| `public_derive_operations` | 2 |
| `delegating_operations` | 2 |
| `identity_free_loads` | 2 |
| `named_for_its_kind` | 2 |
| `public_operation_names` | 2 |
| `lifecycle_operations` | 2 |
| `drives_a_screen` | 2 |

### Entity — 2 nodes

| Fact | Nodes that record it |
|---|---|
| `bases` | 2 |
| `stereotypes` | 2 |
| `method_count` | 2 |
| `operation_shapes` | 2 |
| `property_names` | 2 |
| `held_fields` | 2 |
| `constructs` | 2 |
| `composes_peers` | 2 |
| `peer_names` | 2 |
| `module_helpers` | 2 |
| `prose_comment` | 2 |
| `prototype_swap` | 2 |
| `bold_interaction_lines` | 2 |
| `bold_invariant_lines` | 2 |
| `peer_private_operations` | 2 |
| `public_derive_operations` | 2 |
| `delegating_operations` | 2 |
| `identity_free_loads` | 2 |
| `named_for_its_kind` | 2 |
| `public_operation_names` | 2 |
| `lifecycle_operations` | 2 |
| `drives_a_screen` | 2 |

### Repository — 2 nodes

| Fact | Nodes that record it |
|---|---|
| `bases` | 2 |
| `stereotypes` | 2 |
| `method_count` | 2 |
| `operation_shapes` | 2 |
| `property_names` | 2 |
| `held_fields` | 2 |
| `constructs` | 2 |
| `composes_peers` | 2 |
| `peer_names` | 2 |
| `module_helpers` | 2 |
| `prose_comment` | 2 |
| `prototype_swap` | 2 |
| `bold_interaction_lines` | 2 |
| `bold_invariant_lines` | 2 |
| `peer_private_operations` | 2 |
| `public_derive_operations` | 2 |
| `delegating_operations` | 2 |
| `identity_free_loads` | 2 |
| `named_for_its_kind` | 2 |
| `public_operation_names` | 2 |
| `lifecycle_operations` | 2 |
| `drives_a_screen` | 2 |

### BoundedContext — 1 nodes

| Fact | Nodes that record it |
|---|---|
| `has_module_context` | 1 |
| `has_bounded_context` | 1 |
| `modules_heading` | 1 |
| `names_seam` | 1 |
| `names_constraint` | 1 |
| `model_blocks` | 1 |
| `is_a_in_context` | 1 |
| `child_parent_in_context` | 1 |
| `dependencies` | 1 |
| `imported_classes` | 1 |
