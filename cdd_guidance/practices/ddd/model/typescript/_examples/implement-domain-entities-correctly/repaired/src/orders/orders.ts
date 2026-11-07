export class Orders {
  id: string;
  constructor(id: string) {
    this.id = id;
  }
  bill(): string {
    return this.id;
  }
}
