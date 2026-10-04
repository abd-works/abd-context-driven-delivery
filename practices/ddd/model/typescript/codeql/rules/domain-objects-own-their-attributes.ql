/**
 * @name domain-objects-own-their-attributes
 * @kind problem
 * @id paradise/domain-objects-own-their-attributes
 * @problem.severity warning
 */

import javascript

from FieldDefinition field, ClassDefinition owner
where
  field.getDeclaringClass() = owner and
  owner.getName() = "Onboarding" and
  field.getName() = ["simType", "iccid"]
select field,
  "Onboarding." + field.getName() +
    " describes a child aggregate or an application flag. Put the attribute on the object that owns that fact.",
  field
