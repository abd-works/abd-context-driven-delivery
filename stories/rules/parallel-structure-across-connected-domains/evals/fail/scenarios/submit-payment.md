Scenario: Customer submits payment via Web
  Given a Customer with an active Account
  When the Customer submits a Payment of *$250*
  Then the Payment is *accepted*
  And the Confirmation Number is shown

Scenario: Customer submits payment via API
  Given a Customer
  When the Customer POSTs to */v2/payments*
  Then a *201* response is returned
