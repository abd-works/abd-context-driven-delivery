/**
 * @name Example factory exports
 * @description named factories in *.examples.py — the example name and the domain class it constructs.
 * @kind problem
 * @id cdd/practice-graph/example-exports
 */

import python

from Function factory, Return ret, Call call, File file, string className
where
  file = factory.getFile() and
  file.getBaseName().matches("%.examples.py") and
  ret.getScope() = factory and
  call = ret.getValue() and
  className = call.getFunc().(Name).getId()
select factory, factory.getName(), file.getRelativePath(),
  factory.getLocation().getStartLine(), className, factory.getLocation().getEndLine()
