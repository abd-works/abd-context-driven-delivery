---
scanner: explicit_dependencies_scanner.py
---

# Rule: Production Code Explicit Dependencies

Production code must make **all dependencies explicit** through **constructor injection**. Pass every external dependency (config loader, graph, file system abstraction) as a constructor parameter. No hidden global state, no singletons created internally, no service-locator calls. Explicit dependencies make the class trivially testable.

## DO

- Accept every dependency as a constructor parameter.
- Assign to instance attributes immediately.

```python
class Agent:
    def __init__(
        self,
        agent_name: str,
        workspace_root: Path,
        config_loader: ConfigLoader,
        domain_graph: DomainGraph,
    ) -> None:
        self.name = agent_name
        self.workspace_root = workspace_root
        self._config_loader = config_loader
        self._domain_graph = domain_graph
```

## DON'T

- Create dependencies internally or access module-level singletons.

```python
# WRONG: hidden dependencies created inside the constructor
class Agent:
    def __init__(self, agent_name: str) -> None:
        self.name = agent_name
        self._loader = ConfigLoader()          # creates internally
        self._graph = DomainGraph.get_instance()  # global singleton
```
