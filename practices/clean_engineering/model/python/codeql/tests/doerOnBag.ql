/**
 * @kind problem
 * @id cdd/practice-graph/test/doerOnBag
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class doer, Class bag
where doerOnBag(doer, bag)
select doer, doer.getName(), bag
