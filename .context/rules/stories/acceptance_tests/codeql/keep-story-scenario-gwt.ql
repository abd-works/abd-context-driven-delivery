/**
 * @name keep-story-scenario-gwt
 * @kind problem
 * @id cdd/project/keep-story-scenario-gwt
 * @problem.severity warning
 *
 * Playwright test() in an acceptance file that has no story() or scenario().
 */

import javascript

from CallExpr testCall, File file
where
  testCall.getCalleeName() = "test" and
  file = testCall.getFile() and
  file.getBaseName() != "story-test.ts" and
  (
    file.getBaseName().matches("%.spec.ts") or
    file.getBaseName().matches("%.spec.tsx") or
    file.getBaseName().matches("%_story.test.ts") or
    file.getBaseName().matches("%_story.test.tsx")
  ) and
  not exists(CallExpr story | story.getFile() = file and story.getCalleeName() = "story") and
  not exists(CallExpr scenario | scenario.getFile() = file and scenario.getCalleeName() = "scenario")
select testCall,
  "Acceptance tests keep story() / scenario() Given/When/Then instead of flattening into test() cases.",
  testCall
