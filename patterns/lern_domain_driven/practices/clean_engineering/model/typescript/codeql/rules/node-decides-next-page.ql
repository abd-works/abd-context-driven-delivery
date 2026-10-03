/**
 * @name node-decides-next-page
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node method
 * @id clean_engineering/code/node-decides-next-page
 */

import javascript
import subject_filter
import model

from File f, TopLevel top, StringLiteral path, string message, AstNode contributor
where
  routerModuleFile(f) and
  top.getFile() = f and
  inSubject(top) and
  path.getFile() = f and
  path.getValue().matches("/%") and
  not path.getParent() instanceof JsxAttribute and
  message =
    "The node class decides the next page. Keep this path on *Node.destination and have the router return the path those classes produce." and
  contributor = path
select path, message, contributor
