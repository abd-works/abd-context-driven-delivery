/**
 * @name throw-typed-exception-with-message
 * @kind problem
 * @id paradise/throw-typed-exception-with-message
 * @problem.severity warning
 */

import javascript

from ThrowStmt thrown, ObjectExpr bag
where
  thrown.getFile().getRelativePath().regexpMatch(".*(src/domain/|tests/).*") and
  thrown.getExpr() = bag
select thrown,
  "Throw a typed exception with the message. A plain object is not an exception.",
  bag
