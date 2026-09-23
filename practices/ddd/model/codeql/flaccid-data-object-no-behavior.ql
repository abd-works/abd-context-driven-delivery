/**
 * @name flaccid-data-object-no-behavior
 * @kind problem
 * @id cdd/practice-graph/flaccid-data-object-no-behavior
 * @problem.severity warning
 */

import python
import model

from Class bag
where bagClass(bag)
select bag,
  "Type '" + bag.getName() +
    "' is a flaccid data object (properties only). Give the domain type the operations that belong to it."
