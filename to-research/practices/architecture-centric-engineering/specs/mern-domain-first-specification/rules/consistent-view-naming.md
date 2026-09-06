---
scanner: view_naming_scanner.py
---

# Rule: Consistent View Naming

React components that render a domain concept follow a strict naming convention tied to the domain class name. The suffix communicates the component's role. No ad-hoc suffixes, no framework-jargon names.

## The Contract

```
Domain class:        {ClassName}
Container view:      {ClassName}View          (owns state, fetches data, orchestrates)
List presentation:   {ClassName}ListView      (renders a collection)
Card/row item:       {ClassName}CardView      (renders one item in a list)
Detail view:         {ClassName}DetailView    (renders one item with full detail + actions)
Create form:         Create{ClassName}View    (renders a creation form)
Edit form:           Edit{ClassName}View      (renders an edit form)
```

The domain class name is always the stem. The suffix is always `View` (optionally preceded by a role word).

## DO

- Use the domain class name as the component stem — never abbreviate or synonym it.
- Always end with `View`: `RecipientListView`, `RecipientCardView`, `RecipientDetailView`.
- For the top-level feature container, use `<<Feature>>View` in `app-client/` (e.g. `WirePaymentView.tsx`).
- For the domain-scoped container, use `{ClassName}View` or `{ClassName}ListView`.
- Match the file name to the component name: `RecipientListView.tsx` exports `RecipientListView`.

```typescript
// packages/recipients/client/RecipientListView.tsx
export function RecipientListView({ onSelect }: Props) { ... }

// packages/recipients/client/RecipientCardView.tsx
export function RecipientCardView({ recipient, onSelect }: Props) { ... }

// packages/recipients/client/RecipientDetailView.tsx
export function RecipientDetailView({ recipientId }: Props) { ... }

// packages/recipients/client/CreateRecipientView.tsx
export function CreateRecipientView({ onCreated }: Props) { ... }
```

## DON'T

- Use inconsistent suffixes: `RecipientList`, `RecipientCard`, `RecipientDetail`, `CreateRecipientForm`.
- Drop the `View` suffix: `RecipientSelector`, `RecipientPicker`, `RecipientPanel`.
- Use framework jargon: `RecipientContainer`, `RecipientWrapper`, `RecipientPage`, `WirePaymentPage`.
- Abbreviate the domain name: `RecList`, `RecCard`, `RecDtl`.
- Mix naming styles in the same module: some with `View`, some without.

```typescript
// WRONG — inconsistent suffixes
export function RecipientList() { ... }       // missing View
export function RecipientCard() { ... }       // missing View
export function CreateRecipientForm() { ... } // Form instead of View

// CORRECT — consistent
export function RecipientListView() { ... }
export function RecipientCardView() { ... }
export function CreateRecipientView() { ... }
```
