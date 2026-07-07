import { expect } from 'vitest'
import type { TierImpl } from '../story-types'
import { runScenario } from '../story-runner'
import { SubmitOrder } from './submit-order-stories'
import { submitOrder, seedCart } from '../../../src/orders'

type S = typeof SubmitOrder.orderAccepted

export class SubmitOrderServer implements TierImpl<S> {
  private response!: Awaited<ReturnType<typeof submitOrder>>

  given = {
    'a Cart CART-1 with one Item': async () => {
      await seedCart({ id: 'CART-1', items: [{ sku: 'BOOK-1' }] })
    },
  }

  when = {
    'the Customer submits the Order': async () => {
      this.response = await submitOrder({ cartId: 'CART-1' })
    },
  }

  then = {
    'the Order is Confirmed': async () => {
      expect(this.response.status).toBe('confirmed')
    },
  }

  async cleanup(): Promise<void> {
    this.response = undefined as never
  }
}

runScenario(SubmitOrder.story, SubmitOrder.orderAccepted, () => new SubmitOrderServer())
