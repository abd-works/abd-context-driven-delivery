/**
 * @name use-explicit-dependencies
 * @kind problem
 * @id cdd/practice-graph/use-explicit-dependencies
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls, Function init, Class constructed
where
  inSubject(cls) and
  ownerClass(init, cls) and
  constructsTypeInInit(init, constructed)
select cls,
  "Class '" + cls.getName() + "' constructs '" + constructed.getName() + "' inside __init__.",
  init
