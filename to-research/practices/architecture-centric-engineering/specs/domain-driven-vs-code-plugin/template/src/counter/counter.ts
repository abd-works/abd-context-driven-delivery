// counter/counter.ts — ICounter interface + Counter (root) and Foo (child)

export interface IFoo {
  bar: string;
}

export interface HydrateData {
  total?: number;
  fooBar?: string;
}

/** Shared interface: Counter, CounterServer, CounterView, and client domCounter implement this. CLI output adapters implement ICounterOutputAdapter instead. */
export interface ICounter {
  count(amount: number | string): void;
  reset(): void;
  readonly total: number;
  foo: IFoo;
  hydrate?(data: HydrateData): void;
}

export class Foo implements IFoo {
  bar: string = "";
}

export class Counter implements ICounter {
  private _total: number = 0;
  foo: Foo = new Foo();

  count(amount: number | string): void {
    this._total += Number(amount) || 0;
  }

  get total(): number {
    return this._total;
  }

  reset(): void {
    this._total = 0;
  }

  hydrate(data: HydrateData): void {
    if (data.total !== undefined) this._total = data.total;
    if (data.fooBar !== undefined) this.foo.bar = data.fooBar;
  }
}
