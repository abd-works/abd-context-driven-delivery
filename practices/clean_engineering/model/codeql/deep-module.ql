/**
 * @name deep-module
 * @kind problem
 * @id cdd/practice-graph/deep-module
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module m
where inSubject(m) and firstClassModule(m) and shallowModule(m)
select m,
  "Module exposes " + publicClassCount(m).toString() + " of " +
    classCount(m).toString() + " classes publicly.", m
