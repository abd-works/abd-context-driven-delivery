---
scanner: clear_parameters_scanner.py
---

### Rule: Use Clear Function Parameters

Prefer 0-2 parameters. Use parameter objects for more. Avoid boolean flag parameters.

#### DO

- Use a dataclass or destructured object for complex configuration.
- Separate export functions instead of switching on a flag.

```python
from dataclasses import dataclass

@dataclass
class ConnectionOptions:
    host: str
    port: int
    timeout_ms: int = 2000

def connect(opts: ConnectionOptions): ...

def export_csv(data): return to_csv(data)   # separate functions, not flags
def export_json(data): return to_json(data)
```

```javascript
export function connect({ host, port, timeoutMs = 2000 }) {
  // clear, named parameters
}

export function exportCsv(data) { return toCsv(data); }   // separate, not flag-based
export function exportJson(data) { return toJson(data); }
```

#### DON'T

- Pass boolean flags that change function behavior.
- Exceed 3 positional parameters.

```python
def export_report(data, is_csv: bool):         # WRONG: boolean flag
    return to_csv(data) if is_csv else to_json(data)

def render(chart, dark, pretty, borders): ...  # WRONG: too many parameters
```

```javascript
function exportReport(data, isCsv) {           // WRONG: boolean flag
  return isCsv ? toCsv(data) : toJson(data);
}

function render(chart, dark, pretty, borders) { }  // WRONG: too many parameters
```
