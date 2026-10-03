/**
 * @name epic-package-screens-only
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node module
 * @id clean_engineering/code/epic-package-screens-only
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
  exists(File artifact, TopLevel top |
    artifact = top.getFile() and
    inSubject(top) and
    epicPackagePath(artifact.getRelativePath()) and
    (
      artifact.getBaseName().matches("%-node.ts") or
      artifact.getBaseName().matches("%-server.ts") or
      artifact.getBaseName().matches("%-client.tsx") or
      artifact.getRelativePath().regexpMatch("packages/[^/]+/data/[^/]+\\.json") or
      artifact.getRelativePath().regexpMatch("packages/[^/]+/.+/data/[^/]+\\.json") or
      artifact.getRelativePath().regexpMatch("packages/[^/]+/.+/source/[^/]+\\.ts")
    ) and
    subject = top and
    contributor = top and
    message =
      "Domain tier or lowdb data '" + artifact.getRelativePath() +
        "' belongs under src/<domain>/, not inside packages/<epicSlug>/."
  )
select subject, message, contributor
