---
scanner: property_encapsulation_code_scanner.py
---

### Rule: Enforce Encapsulation

Hide implementation details. Private attributes use `_` prefix (Python) or `#` private fields (JS). Expose domain behavior, not raw data.

#### DO

- Prefix implementation details with `_` or use `#` private fields.
- Expose behavior through domain methods, not internal attributes.

```python
class Inventory:
    def __init__(self, repo):
        self._repo = repo                   # private

    def adjust_many(self, changes: list):
        for sku, delta in changes:
            self._adjust_one(sku, delta)    # private helper

    def _adjust_one(self, sku: str, delta: int):
        self._repo.update_stock(sku, delta)
```

```javascript
export class Inventory {
  #repo;                                    // private field

  constructor(repo) {
    this.#repo = repo;
  }

  async adjustMany(changes) {
    for (const { sku, delta } of changes) {
      await this.#adjustOne(sku, delta);    // private helper
    }
  }
}
```

#### DON'T

- Expose internal attributes as public fields.
- Let callers access or mutate implementation details.

```python
class Inventory:
    def __init__(self):
        self.repo = Repository()            # WRONG: public implementation detail
        self.cache = {}                     # WRONG: exposed internal state
```

```javascript
export class Inventory {
  constructor() {
    this.repo = new Repository();           // WRONG: public implementation detail
    this.cache = {};                        // WRONG: exposed internal state
  }
}
```
