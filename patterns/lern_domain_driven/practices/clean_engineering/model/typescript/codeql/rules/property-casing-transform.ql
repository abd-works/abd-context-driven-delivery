/**
 * @name property-casing-transform
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node property
 * @id clean_engineering/model/property-casing-transform
 */

import javascript
import subject_filter
import model

from AstNode subject, string name, string message, AstNode contributor
where
  inSubject(subject) and
  (
    subject.getFile().getRelativePath().regexpMatch("src/.*") or
    subject.getFile().getRelativePath().regexpMatch("packages/.*")
  ) and
  not subject.getFile().getRelativePath().matches("%node_modules%") and
  (
    exists(VarAccess acc | subject = acc and name = acc.getName())
    or
    exists(PropAccess acc | subject = acc and name = acc.getPropertyName())
    or
    exists(FieldDefinition field | subject = field and name = field.getName())
  ) and
  name.regexpMatch("^[a-z]+_[a-z0-9_]+$") and
  not name.matches("@%") and
  message = "Property '" + name + "' uses snake_case. TypeScript properties must be camelCase." and
  contributor = subject
select subject, message, contributor
