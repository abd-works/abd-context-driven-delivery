export function loadOrder(ctx: { ordersRepository: { load: (id: string) => unknown } }) {
  return ctx.ordersRepository.load("1");
}
