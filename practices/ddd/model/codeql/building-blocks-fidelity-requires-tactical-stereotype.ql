/**
 * @name building-blocks-fidelity-requires-tactical-stereotype
 * @kind problem
 * @id cdd/practice-graph/building-blocks-fidelity-requires-tactical-stereotype
 * @problem.severity warning
 */

import python
import model

from Class cls
where missingTacticalStereotype(cls)
select cls,
  "Class '" + cls.getName() +
    "' is missing a tactical stereotype (Entity, ValueObject, Repository, …).", cls
