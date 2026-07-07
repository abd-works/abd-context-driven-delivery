Scenario: Payment is accepted within balance
  Given a **Customer** with an active **Account**
  When the Customer submits a Payment of *$250*
  Then the Payment is *accepted*
  And the Account balance is reduced by *$250*
