# Snackbar

Module-scoped error-snackbar singleton used by mutation hooks and `QueryCache.onError`. It exists because `QueryCache.onError` runs outside `RecoilRoot` and cannot use a Recoil-aware notification mechanism; a module-scoped reference is the only shape that works.

Used by every mutation hook (Onboarding's `useCustomer`, Self-Care's `useCustomer`, `usePayment`, and others) and by the global TanStack Query error handler registered in `App.tsx`.

**`enqueueSnackbarError({ message })`** -- called when a `request()` result is `{ success: false }` or when TanStack Query bubbles an error from `useCatalog`; surfaces an error toast via notistack.

**`setSnackbarRef()`** -- called from `SnackbarProvider` at mount to hand the notistack `enqueueSnackbar` function to the module; before that point the function is a no-op.

```typescript
// src/utils/snackbar/snackbar.ts
let snackbarRef: SnackbarRef = () => {}

export function setSnackbarRef(ref: SnackbarRef) {
  snackbarRef = ref
}

export function enqueueSnackbarError({ message }: { message: string }) {
  snackbarRef(message, { variant: 'error' })
}
```
