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
  exists(File f, StringLiteral path |
    routerModuleFile(f) and
    path.getFile() = f and
    inSubject(path) and
    path.getValue().regexpMatch("^/[^/]+/.+") and
    not path.getParent() instanceof JsxAttribute and
    subject = path and
    contributor = path and
    message =
      "The node class decides the next page. Keep this path on *Node.destination and have the router return the path those classes produce."
  )
  or
  exists(File f, Function fn |
    routerModuleFile(f) and
    fn.getFile() = f and
    inSubject(fn) and
    fn.getName() = "destination" and
    subject = fn and
    contributor = fn and
    message =
      "The node class decides the next page. The router is a shell: it picks a domain and returns the path the node produces."
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
