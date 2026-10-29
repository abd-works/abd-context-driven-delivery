/**
 * @name json stores
 * @kind problem
 * @id cdd/lern/ddd/nodes/json-store
 */

import javascript
import lern

from File file, string slug
where jsonStoreFile(file, slug)
select jsonStoreId(file), file.getBaseName(), "JsonStore", "ddd", fileSlash(file.getRelativePath()), 1, 1,
  "implementation"
