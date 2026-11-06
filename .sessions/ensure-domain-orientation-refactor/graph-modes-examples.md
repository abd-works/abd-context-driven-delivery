# Graph second model: the two fixes, shown on real code

Three examples from the code as it is now, each shown three ways: **today**, **Mode A** (attach the parsed object), and **Mode B** (the parsers register straight into the real graph). The Mode A and Mode B code is a sketch of the change, not working code.

---

## Example 1: a Clean Engineering rule reads a measurement of an operation

The rule `keep-operations-small-focused` (`cdd_guidance/practices/clean_engineering/model/rules_shared/operation_checks.py:108`) fails an operation longer than 20 lines.

### Today
The TypeScript parser builds an `Operation`, which is already a `BoundNode`, and measures it: it sets `line_count`, `max_control_flow_depth`, `has_bare_catch`, and so on. The loader then copies 21 of those attributes, chosen by the `_OPERATION_FACTS` name list, into a dict on a second, generic `Node`:

```python
# harness/graph/working_copy.py:556 (_class_fact)
op_id = f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}"
operation.load_span_facts("\n".join(lines[start - 1 : end]))
signature = {"owner": cls.name, "parameters": [[p.name, (p.type_hint or "").strip()] for p in operation.parameters]}
op_row = [op_id, operation.name, "Operation", "clean_engineering", relative, start, end]
nodes.append(_fact_row(op_row, _facts_of(operation, _OPERATION_FACTS, signature)))   # copy into a JSON dict
```

`apply_nodes` turns that list into a new `Node`, and the rule reads the copy back by name:

```python
class KeepOperationsSmall(PracticeGraphRule):
    def check(self, node, context):
        size = node.get_fact("line_count") or _line_span(node)    # reads node.data["line_count"]
```

The `Operation` object is thrown away. If someone adds a measurement to `Operation` and forgets `_OPERATION_FACTS`, no rule ever sees it.

### Mode A: the node holds the parsed operation
The loader keeps its id, its file-qualified naming, and its choice of which operations to show. It hands the node the object instead of a copy:

```python
op_id = f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}"   # unchanged
node = practice.add_node(op_id, "Operation", operation.name, Source(relative, start, end), model=operation)
```

`Node.get_fact` reads the object when the node has one, and the saved dict when it doesn't (a graph reloaded from `graph.json`):

```python
def get_fact(self, key, default=None):
    if self.model is not None and key in type(self.model).graph_facts:
        return getattr(self.model, key)
    ...  # the existing data / ancestor lookup, for graphs loaded from graph.json
```

`Operation` declares which of its attributes are saved with the graph, e.g. `graph_facts = ("line_count", "max_control_flow_depth", ...)`, and `_OPERATION_FACTS` in working_copy.py is deleted. **The rule does not change.** The explorer shows the same nodes with the same ids.

### Mode B: the operation is the graph node
The parser is given the real graph, so every `Operation` it builds is a node in the explorer:

```python
model = TypeScriptCleanEngineeringModel(graph=practice.graph).parse(text)   # no copying step
```

The rule reads the attribute directly:

```python
size = node.line_count or _line_span(node)
```

What changes in the explorer:
- **Ids:** `BoundNode` names nodes `clean_engineering:Operation:{name}`, with `:2`, `:3` for repeats. `move_next` on Ticket in ticket.py and `move_next` on another class become `…:move_next` and `…:move_next:2`, so ids depend on load order rather than on file and class.
- **Which nodes show:** the loader skips constructors and `_private` operations today (`working_copy.py:543-546`). The parser builds all of them, so Ticket's `_reopen`, `_mark`, `_enter`, `_folder` and the rest appear unless the parser grows that filter.
- **Edge order:** edges come from `BoundNode._edge_order` and `sync_schema_edges`, not from the loader's numbering. `invokes` sorts at 5 instead of 12, and the loader's `owns` and `properties` edges go away unless the parser adds them.
- **Saved graphs:** every saved `graph.json` has the old ids, so saved graphs must be rebuilt, and the explorer app's tests that name ids must change.

---

## Example 2: a rule re-parses the file to find the operation it is checking

`RuleCheckContext.span(node)` (`harness/graph/rule_context.py:55`) needs an operation's exact start and end lines.

### Today
The rule context reads the file again, parses it again, and searches the new parse for a class and operation by name. It gets the owning class's name by splitting the node id:

```python
def ce_operation(self, node):
    model = self.clean_engineering_model(node)        # channel().parse(text): a second parse of the file
    owner = _owner_class_name(node)                   # node_id.split(":")[-1] → "Ticket"
    for module in model.modules:
        for oclass in module.classes:
            if owner and oclass.name != owner:
                continue
            for op in oclass.operations:
                if op.name == node.name ...:          # match by name
                    return oclass, op
```

A class name containing a dot, or two operations with the same name (an overload or a getter/setter pair), finds the wrong one.

**Correction, found while doing Mode A:** nothing called `span`, `ce_operation`, `ce_class`, `ce_parameter` or `clean_engineering_model`, so Clean Engineering files were not actually parsed twice. That code was dead and has been deleted. The one live use of the id split, `_operation_name_from_param_node` in `typed_and_comments.py`, now reads the parameter's `operation_name` fact. The second parse that did run was the Stories one in Example 3.

### Mode A
```python
def span(self, node):
    model_span = operation_source_span(node.model)    # the operation the loader parsed
```
`ce_operation`, `ce_class`, `ce_parameter`, `clean_engineering_model`, `_owner_class_name` and `_operation_name_from_param_node` are deleted. The owning class is `node.model`'s own class, not a piece of the id.

### Mode B
```python
model_span = operation_source_span(node)              # node is the Operation
```
The same deletions as Mode A.

---

## Example 3: a Stories rule looks a scenario up in a different parse

The rule `examples-trace-domain-model` (`cdd_guidance/practices/stories/rules/scenarios.py:95`) fails a scenario that names domain concepts but has no examples table.

### Today
The loader parses the story **tests** with `TypeScriptStoryModel` (`working_copy.py:767`) and writes Epic, Story, Scenario and Step nodes from that model. The rule then loads the story **map** with a different parser, `StoryModel.load(source_root)` (`rule_context.py:160`), and finds the scenario by name:

```python
scenario = scenario_for_graph_node(node, context)    # StoryModel.load(...), then the first scenario named node.name
story = story_of(context.story_model(), scenario)    # walks every epic again to find the owner
```

That causes two real problems:
- The rule can check a different scenario from the one the explorer shows: the map's version rather than the test's, or nothing at all when the map does not have it.
- Two stories with a scenario of the same name, such as "Happy path", both resolve to the first one, so one is checked twice and the other never.

Steps are matched the same way, by keyword and text (`story_model_lookup.step_from_model`).

### Mode A
`GraphStoryModel` (`graph_story_model.py`) already holds every `Scenario` and `Story` while it writes the nodes. It attaches them:

```python
node = practice.add_node(node_id, "Scenario", scenario.name, source, model=scenario)
```

```python
scenario = node.model
story = node.model.story            # the Story that owns it, set when the parser built it
```

`story_model_lookup.py` is deleted, and `context.story_model()` and its second parse go away. The rule checks exactly the scenario the explorer shows.

### Mode B
The `Scenario`, `Story` and `Step` objects are themselves the nodes (they are `BoundNode`s already), so:

```python
scenario = node
story = node.story
```

The explorer changes as in Example 1: ids become `stories:Scenario:{name}` with `:2` for repeats, in place of the file-qualified `stories:Scenario:{file}:{name}`. That makes every "Happy path" scenario a load-order suffix.

---

## The two data structures, dumped from real code

`BacklogItem.start` in `harness/kanban/backlog_item.py`, loaded with `Graph().load_files(..., ["clean_engineering"], [that file])`.

### Today: what the graph holds (`harness.graph.graph.Node`)
```
node_id : clean_engineering:Operation:harness/kanban/backlog_item.py:start:BacklogItem
type    : Operation        name: start        source: harness/kanban/backlog_item.py 104-111
data    : { line_count: 8, max_control_flow_depth: 1, has_bare_catch: false, ...21 measurements...,
            callees: [exists, is_dir, _ticket_brought_back, _ticket_opened, keep_file],
            owner: "BacklogItem", parameters: [[scope,str],[path,str]],          <- from the code
            interactions: [Ticket.create, Ticket.keep_file],
            model_parameters: [...], model_returns: "Ticket",
            model_file: "harness/kanban/.context/kanban-model.md" }                <- from the model markdown
```
Saved in graph.json as one flat record: `[id, name, type, practice, file, line, end_line, "", "<that data as a JSON string>"]`.

### The parsed object the loader builds and discards (`clean_engineering.model.operation.Operation`, a `BoundNode`)
```
node_id : clean_engineering:Operation:start          <- id from its own throwaway Graph()
source  : . 1-1                                      <- not set; the real lines are in line/end_line
attributes: return_type "Ticket", description "Start the backlog item ...", callees [...],
            invariants [], line 104, end_line 111, line_count 8, body <CodeBody>,
            constructed_types [], is_property/is_static/is_classmethod, max_control_flow_depth 1,
            has_bare_catch, swallows_exceptions, private_reach False, ... parameters (objects)
```

### What the dump shows
- **The same measurements live twice.** `data` is a copy of the object's attributes, chosen by `_OPERATION_FACTS`.
- **They already disagree.** `private_reach` is `True` in the node and `False` in the object, because the loader runs `load_span_facts` again on the line span after parsing.
- **The node mixes two sources.** `model_*` and `interactions` come from `kanban-model.md`, not from the code. In Mode A these stay in `data` (or move to a second model object); only the code measurements move to `node.model`.
- **The parser builds 19 operations; the loader keeps 7.** The 12 it drops are `__init__` ×2, `_write`, `path`, `path_from_project`, `title`, `column`, `text`, `last_activity`, `_held_ticket_folder`, `_ticket_brought_back` and `_ticket_opened`. In Mode B all 19 become nodes unless the parser filters them.
- **The object's own source is empty.** In Mode B the parser has to fill `source` with the file and lines before the explorer can use it.

### Mode A: the same node, holding the object
```
Node  node_id clean_engineering:Operation:harness/kanban/backlog_item.py:start:BacklogItem   (unchanged)
      source  harness/kanban/backlog_item.py 104-111                                        (unchanged)
      data    { owner, interactions, model_parameters, model_returns, model_file }          (model-markdown facts only)
      model ──► Operation(line_count 8, max_control_flow_depth 1, callees [...], ...)       (the parsed object; one copy)
```
`get_fact("line_count")` reads `node.model.line_count`. graph.json still saves the measurements, which `Operation.graph_facts` lists, so a reloaded graph without `model` still answers.

### Mode B: the object is the node
```
Operation  node_id clean_engineering:Operation:start        (or :start:2 if another class has one)
           source  must be set by the parser to backlog_item.py 104-111
           line_count 8, callees [...], ...                  (attributes, no data dict)
           edges   from BoundNode._edge_order, not the loader's numbering
```

---

## Summary

| | Today | Mode A | Mode B |
|---|---|---|---|
| Where a rule gets a measurement | a copied dict, by name | the parsed object, through the node | the node itself |
| Files parsed per load | twice (loader, then rule context) | once | once |
| Name lists in working_copy.py (`_CLASS_FACTS`, `_OPERATION_FACTS`, …) | yes | deleted; each model class declares what it saves | deleted |
| Node ids | file-qualified | unchanged | `practice:Type:name` plus load-order suffixes |
| Private operations and constructors in the explorer | hidden | hidden | shown, unless the parser filters them |
| Edge order | the loader's numbering | unchanged | `BoundNode` and schema numbering |
| Saved `graph.json` | — | still loads | must be rebuilt |
| Explorer app and its tests | — | unchanged | ids, edges and tests change |
| Rule code | `node.get_fact("x")` plus re-parse helpers | `get_fact` unchanged; re-parse helpers become `node.model` | `node.x` |

Mode A fixes the real defects: two parses per file, name-matched lookups that pick the wrong object, and fact lists that drift from the model. It keeps everything the explorer and saved graphs depend on. Mode B goes further and removes the loader's node layout too, which only pays off once the parsers produce file-qualified ids and filter what the explorer shows. Mode A does not rule out Mode B later.
