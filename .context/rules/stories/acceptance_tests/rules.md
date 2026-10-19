```yaml
alwaysApply: false
globs: "**/*_story.test.*,**/*story_test*,**/*story-test*,**/*.spec.ts,**/*.spec.tsx,**/*.client.ts,**/*.server.ts,**/*.e2e.ts,**/*.base.ts,**/*.test.ts,**/*.test.tsx"
```

- **`keep-story-scenario-gwt`** - Keep acceptance tests as named `story()` / `scenario()` Given/When/Then, and drive Playwright from those steps in one story file, because flattening the same behaviour into untitled `test()` cases or a parallel `server.test.ts` plus client story drops the executable specification.
- **`one-playwright-story-file`** - Keep one Playwright `*_story.test.tsx` per story, plus its markdown and the shared pml-domain helper, because a client/server/e2e/base helper quartet or leftover unit tests beside that file re-test the same story.
