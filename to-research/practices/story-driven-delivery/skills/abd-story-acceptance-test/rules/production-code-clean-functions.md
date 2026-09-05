# Rule: Production Code Clean Functions

Production code functions must do **one thing**, stay **under 20 lines**, operate at a **single level of abstraction**, and have **no hidden side effects**. The function name must fully describe what it does. Extract multiple concerns into separate functions.

## DO

- Each function has a single, named purpose.
- Functions compose to build complexity.

```python
def load_config(self, path: Path) -> dict:
    """Load configuration from file."""
    return json.loads(path.read_text())

def validate_config(self, config: dict) -> bool:
    """Validate configuration has required keys."""
    return all(key in config for key in ('name', 'workspace'))

def initialize_from_config(self, path: Path) -> None:
    """Initialize agent from configuration file."""
    config = self.load_config(path)
    if not self.validate_config(config):
        raise ValueError(f'Invalid config at {path}')
    self._apply_config(config)
```

## DON'T

- Write functions that load, validate, apply, and log in the same body.
- Exceed 20 lines in a single function.

```python
# WRONG: function does too many things
def setup(self, path: Path) -> None:
    config = json.loads(path.read_text())   # load
    if 'name' not in config:                # validate
        raise ValueError('Invalid')
    self.name = config['name']              # apply
    logger.info(f'Initialized {self.name}') # log
    self._send_metrics()                    # side effect
```
