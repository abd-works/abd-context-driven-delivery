/**
 * @name shape-classes-around-resources
 * @kind problem
 * @id cdd/practice-graph/shape-classes-around-resources
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class doer, Class bag
where inSubject(doer) and doerOnBag(doer, bag)
select doer,
  "Class '" + doer.getName() + "' acts on bag '" + bag.getName() + "'.", bag
