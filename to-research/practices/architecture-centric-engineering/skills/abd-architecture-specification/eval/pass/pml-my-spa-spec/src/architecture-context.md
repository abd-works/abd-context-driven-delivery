# Mechanism: App Bootstrap

### Overview

App Bootstrap is the mechanism by which the React application becomes a running, fully-providered tree before any feature module renders. It splits into two files with two different shapes: `main.tsx` is imperative -- it conditionally initialises third-party SDKs (GA4, GTM, Hotjar, PageSense, console suppression) before calling `createRoot().render(<App />)`; `App.tsx` is declarative -- it assembles the provider stack and creates module-scoped singletons (`QueryClient`, `GrowthBook`) outside the component tree so they survive `<App />` re-renders.

### File Structure

```
src/
+-- main.tsx                 <- DOM mount; conditional vendor init in non-development
+-- App.tsx                  <- provider stack composition; QueryClient + GrowthBook singletons
+-- config/
|   +-- env.ts               <- module evaluated here first; requireEnv runs before main.tsx returns
+-- utils/
|   +-- logger/disableConsole/   <- called from main.tsx in non-development environments
|   +-- analytics/AnalyticsWrapper.tsx   <- mounts inside RecoilRoot; captures UTM
|   +-- snackbar/snackbar.ts             <- module-scoped enqueueSnackbarError used by QueryCache.onError
```

### Participants

| Class / Module             | Responsibility                                                                                          | Collaborators                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `main.tsx`                 | DOM mount; conditional GA4 / GTM / Hotjar / PageSense / `disableConsole` init in non-development        | `env`, `App`, vendor SDKs                      |
| `App.tsx`                  | Provider stack assembly; module-scope `QueryClient` and `GrowthBook` instances; `loadFeatures()` fire-and-forget | `QueryClient`, `GrowthBook`, `RecoilRoot`, `Router` |
| `QueryClient` (singleton)  | TanStack Query in-process cache plus global `onError` handler                                           | `enqueueSnackbarError`                         |
| `GrowthBook` (singleton)   | Feature flag instance fetched from CDN at startup                                                       | `env.growthbook`                               |
| `AnalyticsWrapper`         | Reads `window.location.search`, writes `utmAtom` once after mount                                       | `utmAtom`, `query-string`                      |

### Flow

```mermaid
sequenceDiagram
    participant Browser
    participant main as "main.tsx"
    participant App as "App.tsx"
    participant Analytics as "AnalyticsWrapper"
    participant Router as "Router.tsx"

    Browser->>main: load index.html; evaluate bundle
    main->>main: if env.environment !== 'development' -> disableConsole(), ReactGA.initialize(), TagManager.initialize(), hotjarInit(), pageSenseInit()
    main->>App: createRoot().render(<App />)
    App->>App: module scope -- QueryClient + GrowthBook; growthbook.loadFeatures() (fire-and-forget)
    App->>Analytics: mounts inside RecoilRoot
    Analytics->>Analytics: useEffect parses window.location.search -> writes utmAtom
    App->>Router: renders with full provider stack established
```

### Rules

- **Pre-mount work lives in `main.tsx` only.** No feature module may import or call vendor `initialize()` functions; the audit point is `main.tsx`.
- **Singletons live at module scope.** `QueryClient` and `GrowthBook` are constructed once in `App.tsx`'s top-level scope, not inside the component body, so they survive re-renders.
- **Provider nesting order is fixed** -- `LocalizationProvider` -> `QueryClientProvider` -> `RecoilRoot` -> `AnalyticsWrapper` -> `GrowthBookProvider` -> `ThemeProvider` -> `SnackbarProvider` -> `BrowserRouter`. `AnalyticsWrapper` must be inside `RecoilRoot` so it can write `utmAtom`; `QueryCache.onError` cannot read Recoil because `QueryClient` is outside `RecoilRoot`, which is why it uses the module-scoped `enqueueSnackbarError`.
- **Vendor init is gated.** All analytics SDKs (and `disableConsole`) only run when `env.environment !== 'development'` -- development keeps console open and avoids polluting marketing dashboards.
- **Tests never use the production `QueryClient` singleton.** Component tests wrap their tree in a fresh `new QueryClient()` per test.

### Canonical Patterns

```typescript
async function bootstrap() {
  if (env.environment !== 'development') {
    disableConsole()
    ReactGA.initialize(env.google.gaId, { gaOptions: { siteSpeedSampleRate: 100 } })
    TagManager.initialize({ gtmId: env.google.gtmId })
    hotjarInit()
    pageSenseInit()
  }
  const rootElement = document.getElementById('root')
  rootElement && createRoot(rootElement).render(<App />)
}
void bootstrap()
```
