/**
 * @name node-decides-next-page
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node method
 * @id clean_engineering/model/node-decides-next-page
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
  exists(CallExpr redirect, StringLiteral path |
    (
      routerModuleFile(redirect.getFile()) or
      routeFile(redirect.getFile()) or
      redirect.getFile().getBaseName().matches("%-redirect.tsx")
    ) and
    inSubject(path) and
    redirect.getCalleeName() = "redirect" and
    path = redirect.getAnArgument() and
    path.getValue().regexpMatch("^/.+") and
    not path.getValue().regexpMatch("^/api/.*") and
    subject = path and
    contributor = path and
    message =
      "The node class decides the next page. Keep this path on *Node.destination and have the router return the path those classes produce."
  )
  or
  exists(CallExpr repo |
    inSubject(repo) and
    (nodeFile(repo.getFile()) or serverFile(repo.getFile())) and
    repo.getCalleeName() = "load" and
    repo.toString().matches("repo.%") and
    subject = repo and
    contributor = repo and
    message =
      "The node class decides the next page. Route handlers ask the node class instead of calling the repository."
  )
select subject, message, contributor
