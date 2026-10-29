/**
 * @name node-decides-view
 * @kind problem
 * @id cdd/lern/ddd/edges/node-decides-view
 */

import javascript
import lern

from ClassDefinition node, Function view, StringLiteral lit, string base
where
  domainNodeClass(node) and
  domainView(view) and
  lit.getFile() = node.getFile() and
  base = view.getFile().getBaseName().regexpReplaceAll("\\.tsx$", "") and
  lit.getValue().matches("%/" + base + "%")
select domainNodeId(node), domainViewId(view), "decides", 9, "relationship"
