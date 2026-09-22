/**
 * @name keep-classes-single-responsibility
 * @kind problem
 * @id cdd/practice-graph/keep-classes-single-responsibility
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls, Function method
where
  inSubject(cls) and
  tooManyPublicMethods(cls) and
  publicMethod(cls, method)
select cls,
  "Class '" + cls.getName() + "' has " + publicMethodCount(cls).toString() + " public methods.",
  method
