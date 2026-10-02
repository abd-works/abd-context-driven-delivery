/**
 * @name one-playwright-story-file
 * @kind problem
 * @id cdd/project/one-playwright-story-file
 * @problem.severity warning
 *
 * Extra client/server/e2e/base layers or leftover unit tests beside a story acceptance file.
 */

import javascript

predicate isStoryAcceptance(File file) {
  file.getBaseName().matches("%_story.test.ts") or
  file.getBaseName().matches("%_story.test.tsx")
}

predicate isUnderTests(File file) { file.getRelativePath().matches("%/tests/%") }

predicate isLayerHelper(File file) {
  isUnderTests(file) and
  (
    file.getBaseName().matches("%.client.ts") or
    file.getBaseName().matches("%.client.tsx") or
    file.getBaseName().matches("%.server.ts") or
    file.getBaseName().matches("%.server.tsx") or
    file.getBaseName().matches("%.e2e.ts") or
    file.getBaseName().matches("%.e2e.tsx") or
    file.getBaseName().matches("%.base.ts") or
    file.getBaseName().matches("%.base.tsx") or
    file.getBaseName().matches("%_story.server.test.ts") or
    file.getBaseName().matches("%_story.client.test.ts") or
    file.getBaseName().matches("%_story.e2e.test.ts")
  )
}

predicate isLeftoverBesideStory(File extra) {
  exists(File story |
    isStoryAcceptance(story) and
    extra.getParentContainer() = story.getParentContainer() and
    extra != story and
    (
      extra.getBaseName().matches("%.test.ts") or
      extra.getBaseName().matches("%.test.tsx")
    ) and
    not isStoryAcceptance(extra)
  )
}

from File extra
where isLayerHelper(extra) or isLeftoverBesideStory(extra)
select extra,
  "Keep one Playwright *_story.test.tsx per story; extra client/server/e2e/base layers or leftover tests re-test the same story.",
  extra
