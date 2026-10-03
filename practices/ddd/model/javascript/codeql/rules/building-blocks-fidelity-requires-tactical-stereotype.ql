/**
 * @name building-blocks-fidelity-requires-tactical-stereotype
 * @practice ddd
 * @fidelity building_blocks
 * @node class
 * @id ddd/building_blocks/building-blocks-fidelity-requires-tactical-stereotype
 */

import javascript
import model

from ClassDefinition cls
where missingTacticalStereotype(cls)
select cls,
  "Class '" + cls.getName() +
    "' is missing a tactical stereotype (Entity, ValueObject, Repository, …).", cls
