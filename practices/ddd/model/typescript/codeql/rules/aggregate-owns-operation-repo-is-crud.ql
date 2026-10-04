/**
 * @name aggregate-owns-operation-repo-is-crud
 * @kind problem
 * @id paradise/aggregate-owns-operation-repo-is-crud
 * @problem.severity warning
 */

import javascript

from MethodDefinition method, ClassDefinition repo
where
  method.getDeclaringClass() = repo and
  repo.getName().matches("%Repository") and
  method.getName()
      .regexpMatch("validate|submit|getNumbers|searchNumbers|reserve|getIccid|mapInquiryOntoCustomer|payUpFrontFailed|roamingTicketRequired|submitPortability")
select method,
  "Repository method '" + repo.getName() + "." + method.getName() +
    "' names a domain operation. Keep the repository to create, read, update, and delete, and put the operation on the aggregate.",
  method
