/**
 * @name observable-behavior
 * @kind problem
 * @id cdd/practice-graph/observable-behavior
 * @problem.severity warning
 */

import python
import model

from Attribute attr
where privateProbeInExpect(attr)
select attr,
  "Assertion accesses private field '" + attr.getName() +
    "'. Assert observable behavior through the public API."
