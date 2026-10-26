story('Create Unconfirmed User', () => {
  background(({ given }) => {
    scenario('Display Create Account', ({ when, then }) => {
      let accountCredentials: AccountCredentials;
      when('the User proceeds to create an account from the Paradise Mobile website', () => {
        accountCredentials = accountRepository.newAccount();
      });
      then('the User can enter account credentials', () => {
        expect(accountCredentials.isUpdatable).toBe(true);
      })
        .and('the email and password rules are unmet', () => {
          const missing = accountCredentials.missingRequirements();
          expect(missing).toContain(accountCredentials.requirements.emailRequired);
          expect(missing).toContain(accountCredentials.requirements.passwordRequired);
          expect(missing).toContain(accountCredentials.requirements.confirmRequired);
        })
        .and('the customer cannot save the customer account', () => {
          expect(accountCredentials.isPersistable).toBe(false);
        });
    });
      