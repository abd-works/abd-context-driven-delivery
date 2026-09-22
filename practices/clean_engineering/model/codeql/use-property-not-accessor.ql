/**
 * @name use-property-not-accessor
 * @kind problem
 * @id cdd/practice-graph/use-property-not-accessor
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls, Function f
where
  inSubject(cls) and
  ownerClass(f, cls) and
  accessorOperation(f)
select cls, "Class '" + cls.getName() + "' exposes '" + f.getName() + "' as an accessor.", f
