/**
 * @name view-renders-operation
 * @kind problem
 * @id cdd/lern/ddd/edges/view-renders-operation
 */

import javascript
import lern

from Function view, MethodCallExpr call, MethodDefinition method, string slug
where
  domainView(view) and
  call.getEnclosingFunction*() = view and
  call.getCalleeName() = method.getName() and
  slug = fileOf(view).regexpCapture("src/([^/]+)/.*", 1) and
  rootOperation(slug, method)
select domainViewId(view), operationNodeId(method), "renders", 5, "relationship"
