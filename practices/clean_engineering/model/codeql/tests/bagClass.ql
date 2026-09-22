/**
 * @kind problem
 * @id cdd/practice-graph/test/bagClass
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class bag
where bagClass(bag)
select bag, bag.getName()
