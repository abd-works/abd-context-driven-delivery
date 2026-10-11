/**
 * @name client-interacts-entity
 * @kind problem
 * @id cdd/lern/ddd/edges/client-interacts-entity
 */

import javascript
import model
import ddd

from ClassDefinition client, ClassDefinition root, string parent, string child, string slug
where
  domainClient(client, parent, _, _, _, _) and
  slug = domainSlugFromClient(client) and
  dddClass(root, "EntityRoot", child, _, _, _, _) and
  moduleName(root) = slug
select parent, child, "interacts", 5, "relationship"
