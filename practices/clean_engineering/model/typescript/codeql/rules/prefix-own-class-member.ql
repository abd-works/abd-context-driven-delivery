/**
 * @name prefix-own-class-member
 * @kind problem
 * @id paradise/prefix-own-class-member
 * @problem.severity warning
 */

import javascript

predicate ownClassMember(string typeName, string name) {
  typeName = "AccountCredentials" and name = "validationCodeSentAt"
  or
  typeName = "Onboarding" and name = "submitOrder"
  or
  typeName = "Payment" and name = "paymentAttempts"
}

string problemMessage(string typeName, string name) {
  typeName = "AccountCredentials" and
  name = "validationCodeSentAt" and
  result =
    "AccountCredentials.validationCodeSentAt is only used by its own class. Prefix it with _. The account repository may still persist the clock. Leave token, customerId, resendMessage, expectedValidationCode, and validationCodeMessages public when tests or other classes observe them."
  or
  typeName = "Onboarding" and
  name = "submitOrder" and
  result = "Onboarding.submitOrder is only used by Onboarding. Prefix it with _."
  or
  typeName = "Payment" and
  name = "paymentAttempts" and
  result = "Payment.paymentAttempts is only used by Payment. Prefix it with _."
}

from AstNode subject, string message, AstNode contributor
where
  exists(string typeName, string name |
    ownClassMember(typeName, name) and
    message = problemMessage(typeName, name) and
    (
      exists(FieldDefinition field |
        subject = field and
        contributor = field and
        field.getDeclaringClass().getName() = typeName and
        field.getName() = name
      )
      or
      exists(PropAccess access |
        subject = access and
        contributor = access and
        access.getPropertyName() = name and
        access.getFile().getRelativePath().matches("tests/%")
      )
    )
  )
select subject, message, contributor
