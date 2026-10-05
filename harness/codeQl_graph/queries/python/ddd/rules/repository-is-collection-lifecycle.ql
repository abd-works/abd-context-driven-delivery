/**
 * @name repository-is-collection-lifecycle
 * @kind problem
 * @id cdd/ddd/rules/repository-is-collection-lifecycle
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls
where
  rule = "repository-is-collection-lifecycle" and
  cls.getName().matches("%Repository") and
  not exists(Function method |
    method = cls.getAMethod() and
    (
      method.getName() = "add" or method.getName() = "remove" or
      method.getName() = "get" or method.getName() = "find"
    )
  ) and
  node = nodeId("ddd", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' is a repository without collection operations.")
select rule, node, violation
