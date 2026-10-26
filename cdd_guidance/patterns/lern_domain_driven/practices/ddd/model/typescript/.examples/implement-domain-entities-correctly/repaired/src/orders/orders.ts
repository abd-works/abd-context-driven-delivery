export class Orders {
  id: string;
  constructor(id: string) {
    this.id = id;
  }
  bill() {
    return this.id;
  }
}
