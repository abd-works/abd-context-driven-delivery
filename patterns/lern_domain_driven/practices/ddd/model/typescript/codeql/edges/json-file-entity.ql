/**
 * @name json-file-entity
 * @kind problem
 * @id cdd/lern/ddd/edges/json-file-entity
 */

import javascript
import lern

from File file, string slug, ClassDefinition root, string child
where
  jsonStoreFile(file, slug) and
  dddClass(root, "EntityRoot", child, _, _, _, _) and
  moduleName(root) = slug
select jsonStoreId(file), child, "jsonFile", 5, "relationship"
