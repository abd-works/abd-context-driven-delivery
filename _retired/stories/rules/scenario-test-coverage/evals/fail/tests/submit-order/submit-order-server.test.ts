import { describe, expect, it } from 'vitest'
import type { TierImpl } from '../story-types'
import { SubmitOrder } from './submit-order-stories'

type Scenarios = typeof SubmitOrder.orderAccepted

export class SubmitOrderServer implements TierImpl<Scenarios> {
  given = {
    'a Cart CART-1 with one Item': async () => {
      // seed cart
    },
    'an empty Cart CART-2': async () => {
      // seed empty cart
    },
  }

  when = {
    'the Customer submits the Order': async () => {
      // call submitOrder
    },
  }

  then = {
    'the Order is Confirmed': async () => {
      expect(true).toBe(true)
    },
    'an error "Cart is empty" is shown': async () => {
      expect(true).toBe(true)
    },
  }

  async cleanup(): Promise<void> {}
}

// emptyCartRejected scenario is intentionally missing — scanner should flag this
describe(SubmitOrder.story, () => {
  describe(SubmitOrder.orderAccepted.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new SubmitOrderServer()
      // Given
      await tier.given['a Cart CART-1 with one Item']()
      // When
      await tier.when['the Customer submits the Order']()
      // Then
      await tier.then['the Order is Confirmed']()
      await tier.cleanup()
    })
  })
})
