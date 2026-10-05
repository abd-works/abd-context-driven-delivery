/**
 * @name observable-graph-load
 * @kind problem
 * @id cdd/project/observable-graph-load
 * @problem.severity warning
 *
 * Graph-load it() that calls arrangeListedClassChildren instead of naming listed children from CodeQL edges.
 */

import javascript

from CallExpr observation, CallExpr arrange
where
  observation.getCalleeName() = "it" and
  arrange.getCalleeName() = "arrangeListedClassChildren" and
  arrange.getEnclosingFunction() = observation.getArgument(1)
select observation,
  "Name CodeQL graph load as registered nodes, related edges, class child order, and story examples from demonstrates.",
  arrange
