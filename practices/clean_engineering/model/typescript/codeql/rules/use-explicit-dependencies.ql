/**
 * @name use-explicit-dependencies
 * @kind problem
 * @id cdd/ce/rules/use-explicit-dependencies
 */

import javascript
import ce

from string rule, string node, string violation, ClassDefinition cls, NewExpr created
where
  rule = "use-explicit-dependencies" and
  domainClass(cls) and
  node = classId(cls) and
  exists(MethodDefinition ctor |
    ctor.getDeclaringType() = cls and
    ctor.getName() = "constructor" and
    created.getEnclosingFunction() = ctor.getBody() and
    created.getCalleeName() != cls.getName() and
    violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' constructs '" + created.getCalleeName() + "' inside its constructor.")
  )
select rule, node, violation
