# Input traps — abd-ux-ui-implementation

Pre-flight only — not grill questions. Check each trap before writing UI code.

- **Duplicate hunt skipped** — Did you search for existing CSS variables, utility classes, and JS helpers before adding anything new?
- **Inline style temptation** — Are you about to use `style="..."` or a local `<style>` block instead of the central theme?
- **Reinvented control** — Is a custom class solving something Tailwind, Bootstrap, or an existing utility already handles?
- **Copy-paste component** — Will this card, button, or modal appear more than once without a reusable snippet or component?
- **Duplicated DOM logic** — Are you writing another fetch, toggle, or event listener that belongs in a shared utility module?
