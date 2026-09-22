/**
 * @name flaccid-data-object-no-behavior
 * @kind problem
 * @id cdd/practice-graph/flaccid-data-object-no-behavior
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class bag
where inSubject(bag) and bagClass(bag)
select bag, "Class '" + bag.getName() + "' is a field bag with no operations.", bag
