# Catalog Caching

Catalog Caching is the single TanStack Query usage in pml-my. It exists to render the plan catalog without a loading spinner on the SelectPlan (Onboarding) and ChangePlan (Self-Care) pages. The catalog is unauthenticated, session-stable reference data and is fetched once per browser session.

Used by Onboarding (`SelectPlan`) and Self-Care (`ChangePlan`). Uses a direct Axios call rather than the `request()` wrapper because the catalog is unauthenticated and the response is sanitised inside the query function (plans with `price === 0` are filtered out, `' PROMO'` name suffixes are stripped).

**`useCatalog()`** -- called when the SelectPlan or ChangePlan page mounts; returns the cached `Plan[]` immediately on subsequent renders thanks to `staleTime: Infinity`.

**`fetchPlans()`** (private to `useCatalog.tsx`) -- the query function; calls `GET /mv/catalog`, filters and sanitises the response before TanStack Query stores it.

**Why TanStack Query for this one call** -- the catalog is the only piece of state in pml-my that benefits from a session-long stale-while-revalidate cache; all other state is in Recoil. Adding a second TanStack Query usage in the codebase requires an ADR.

**Cache invalidation** -- there is none. The catalog is treated as immutable within a session; a full page refresh is the only way to re-fetch.

```typescript
// src/services/mavenir/useCatalog.tsx
export function useCatalog() {
  return useQuery({
    queryKey: ['catalog'],
    queryFn: fetchPlans,
    staleTime: Infinity,
  })
}
```
