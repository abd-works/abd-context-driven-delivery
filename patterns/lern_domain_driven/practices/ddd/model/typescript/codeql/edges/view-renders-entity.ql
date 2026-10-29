/**
 * @name view-renders-entity
 * @kind problem
 * @id cdd/lern/ddd/edges/view-renders-entity
 */

import javascript
import lern

from Function view, ClassDefinition entity, string child
where
  domainView(view) and
  entityKind(entity, _, child) and
  (
    exists(ClassDefinition client, ImportSpecifier spec |
      spec.getFile() = view.getFile() and
      spec.getLocal().getName() = client.getName() and
      extendsNamed(client, entity.getName())
    )
    or
    exists(ImportSpecifier spec |
      spec.getFile() = view.getFile() and
      spec.getLocal().getName() = entity.getName()
    )
    or
    view.getName().matches("%" + entity.getName() + "View")
  )
select domainViewId(view), child, "renders", 5, "relationship"
