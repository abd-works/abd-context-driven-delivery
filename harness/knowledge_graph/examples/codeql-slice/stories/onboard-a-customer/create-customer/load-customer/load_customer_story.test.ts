// fixture — line numbers align with practice-graph.json for CodeQL join tests
story('Load Customer', () => {
  scenario('Load My Paradise customer and store in session', ({ when, then }) => {
    when('My Paradise loads the customer from Mavenir', () => {
      customerRepository.load('id-1')
    })
    then('the result is a Paradise customer with identity and address', () => {
      expect(customer.identity).toBeDefined()
    })
  })
})
