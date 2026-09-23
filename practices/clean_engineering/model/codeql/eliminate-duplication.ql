/**
 * @name eliminate-duplication
 * @kind problem
 * @id cdd/practice-graph/eliminate-duplication
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function a, Function b
where
  inSubject(a) and
  duplicateOperation(a, b) and
  a.getName() < b.getName()
select a,
  "Operation '" + a.getName() + "' duplicates '" + b.getName() + "'.", b
