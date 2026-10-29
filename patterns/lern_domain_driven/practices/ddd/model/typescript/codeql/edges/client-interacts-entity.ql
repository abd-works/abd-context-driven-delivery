/**
 * @name client-interacts-entity
 * @kind problem
 * @id cdd/lern/ddd/edges/client-interacts-entity
 */

import javascript
import lern

from ClassDefinition client, ClassDefinition root, string child
where
  domainClientClass(client) and
  dddClass(root, "EntityRoot", child, _, _, _, _) and
  extendsNamed(client, root.getName())
select domainClientId(client), child, "interacts", 5, "relationship"
