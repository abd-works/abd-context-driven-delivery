/**
 * @name properties
 * @kind problem
 * @id cdd/ce/nodes/properties
 */

import javascript
import ce

from string className, string name, string base, int start, string path, int end, string hint
where classProperty(className, name, base, start, path, end, hint)
select propertyId(path, name, className), name, "Property", "clean_engineering", slash(path), start,
  end, className, hint
