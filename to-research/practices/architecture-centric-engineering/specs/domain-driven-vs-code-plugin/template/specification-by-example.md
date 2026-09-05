# Specification by Example — Counter / Engine Plugin

These scenarios drive out the Counter/Engine domain behaviour. Each tier (domain, server domain, server view) runs the same behaviour suite with additional tier-specific assertions layered on top.

---

## Story: Count and Reset

**As a** user of the Counter panel
**I want to** click Count and Reset buttons in the webview
**So that** the counter total updates immediately in the UI and persists across extension restarts

### Scenario: Start at zero

```
GIVEN a new Counter
WHEN no operations have been performed
THEN total is 0
```

### Scenario: Count by integer

```
GIVEN a Counter at zero
WHEN count(3) is called
THEN total is 3
```

### Scenario: Count accumulates

```
GIVEN a Counter at zero
WHEN count(3) is called
AND count(2) is called
THEN total is 5
```

### Scenario: Reset returns to zero

```
GIVEN a Counter with total 5
WHEN reset() is called
THEN total is 0
```

---

## Story: Persist Across Restarts (Server Domain)

**As a** user
**I want** my counter total to survive VS Code restarts
**So that** I don't lose my running total when the extension reloads

### Scenario: Count survives reload

```
GIVEN a CounterServer pointing at a file
WHEN count(3) is called
AND a new CounterServer is created pointing at the same file
THEN the new instance reports total 3
```

### Scenario: Reset persists

```
GIVEN a CounterServer with total 5
WHEN reset() is called
AND a new CounterServer is created at the same path
THEN total is 0
```

---

## Story: Sync State to Webview (Server View)

**As a** VS Code webview
**I want** to receive the updated total after every mutation
**So that** the displayed total is always in sync with the extension host

### Scenario: postMessage sent after count

```
GIVEN a CounterView wrapping a Counter
WHEN count(3) is called on the view
THEN panel.webview.postMessage is called with { total: 3 }
AND the rendered HTML contains <span id="total">3</span>
```

### Scenario: postMessage sent after reset

```
GIVEN a CounterView with total 5
WHEN reset() is called
THEN postMessage is called with { total: 0 }
AND getHtml() contains <span id="total">0</span>
```
