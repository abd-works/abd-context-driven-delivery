# Generate — abd-ux-ui-implementation

Produce production UI code that reuses existing tokens, utilities, and patterns with zero duplication.

## When to activate

- Generating new UI components or layouts.
- Adding styles, changing colors, or fixing layouts.
- Writing scripts, DOM manipulation, or event listeners.

## Step 1: Pre-flight search

Before writing any code, use `grep` or search tools to scan project files:

- Existing CSS custom properties (variables), utility classes, and design tokens.
- Existing JS helper files and common event utility modules.

## Step 2: Enforcement rules

### Styles (CSS)

- **Zero inline styles** — never use `style="..."` or inject local `<style>` blocks.
- **Token first** — map colors, font sizes, and spacing to existing global variables (e.g. `var(--color-primary)`). If missing, ask to add to the central theme file first.
- **Framework priority** — when Tailwind or Bootstrap is present, compose existing utilities; do not invent custom classes for solved problems.

### Layouts (HTML)

- **Component separation** — blocks used more than once (card, button, modal) must be reusable snippets or component templates.

### Behavior (JavaScript)

- **Utility exports** — DOM selections, fetches, and toggles belong in a central utility script; do not duplicate event patterns.

## Step 3: Reporting format

Begin every completed task with:

**[DRY Audit Log]** Reused Styles: [x], Reused Logic: [y], Duplication Avoided: [z]
